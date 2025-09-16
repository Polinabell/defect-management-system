/**
 * Диалоги для управления дефектами
 */

import React, { useState, useCallback, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Box,
  Avatar,
  Chip,
  Alert,
  Stack,
  Autocomplete,
  Card,
  CardContent,
  IconButton,
  Stepper,
  Step,
  StepLabel
} from '@mui/material';
import {
  Close as CloseIcon,
  CloudUpload as UploadIcon,
  Image as ImageIcon,
  Delete as DeleteIcon,
  Send as SendIcon
} from '@mui/icons-material';
import { useAppDispatch } from '../../store';
import {
  createDefect,
  updateDefect,
  changeDefectStatus,
  assignDefect,
  Defect
} from '../../store/slices/defectsSlice';

// Константы
const STATUS_OPTIONS = [
  { value: 'new', label: 'Новый', color: '#2196f3' },
  { value: 'in_progress', label: 'В работе', color: '#ff9800' },
  { value: 'review', label: 'На проверке', color: '#9c27b0' },
  { value: 'closed', label: 'Закрыт', color: '#4caf50' },
  { value: 'cancelled', label: 'Отменен', color: '#f44336' }
];

const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Низкий', color: '#4caf50' },
  { value: 'medium', label: 'Средний', color: '#ff9800' },
  { value: 'high', label: 'Высокий', color: '#f44336' },
  { value: 'critical', label: 'Критический', color: '#e91e63' }
];

const SEVERITY_OPTIONS = [
  { value: 'cosmetic', label: 'Косметический', color: '#4caf50' },
  { value: 'minor', label: 'Незначительный', color: '#8bc34a' },
  { value: 'major', label: 'Серьезный', color: '#ff9800' },
  { value: 'critical', label: 'Критический', color: '#f44336' },
  { value: 'blocking', label: 'Блокирующий', color: '#e91e63' }
];

// Workflow steps
const WORKFLOW_STEPS = [
  { key: 'new', label: 'Новый' },
  { key: 'in_progress', label: 'В работе' },
  { key: 'review', label: 'На проверке' },
  { key: 'closed', label: 'Завершен' }
];

// Интерфейсы
interface DefectFormData {
  title: string;
  description: string;
  priority: string;
  severity: string;
  project: number | '';
  category: number | '';
  location: string;
  floor: string;
  room: string;
  assignee?: number | '';
  due_date?: string;
}

interface CreateDefectDialogProps {
  open: boolean;
  onClose: () => void;
  projects: any[];
  categories: any[];
  engineers: any[];
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

interface EditDefectDialogProps {
  open: boolean;
  onClose: () => void;
  defect: Defect | null;
  projects: any[];
  categories: any[];
  engineers: any[];
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

interface StatusChangeDialogProps {
  open: boolean;
  onClose: () => void;
  defect: Defect | null;
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

interface AssignDefectDialogProps {
  open: boolean;
  onClose: () => void;
  defect: Defect | null;
  engineers: any[];
  onSuccess: (message: string) => void;
  onError: (message: string) => void;
}

// Компонент создания дефекта
export const CreateDefectDialog: React.FC<CreateDefectDialogProps> = ({
  open,
  onClose,
  projects,
  categories,
  engineers,
  onSuccess,
  onError
}) => {
  const dispatch = useAppDispatch();
  const [formData, setFormData] = useState<DefectFormData>({
    title: '',
    description: '',
    priority: 'medium',
    severity: 'minor',
    project: '',
    category: '',
    location: '',
    floor: '',
    room: '',
    assignee: '',
    due_date: ''
  });
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const resetForm = useCallback(() => {
    setFormData({
      title: '',
      description: '',
      priority: 'medium',
      severity: 'minor',
      project: '',
      category: '',
      location: '',
      floor: '',
      room: '',
      assignee: '',
      due_date: ''
    });
    setSelectedFile(null);
  }, []);

  const handleClose = useCallback(() => {
    if (!isSubmitting) {
      resetForm();
      onClose();
    }
  }, [isSubmitting, resetForm, onClose]);

  const handleFileSelect = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Проверка размера файла (макс 5МБ)
      if (file.size > 5 * 1024 * 1024) {
        onError('Размер файла не должен превышать 5МБ');
        return;
      }
      
      // Проверка типа файла
      if (!file.type.startsWith('image/')) {
        onError('Можно загружать только изображения');
        return;
      }
      
      setSelectedFile(file);
    }
  }, [onError]);

  const handleSubmit = useCallback(async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!formData.title.trim()) {
      onError('Необходимо указать название дефекта');
      return;
    }
    
    if (!formData.project) {
      onError('Необходимо выбрать проект');
      return;
    }
    
    if (!formData.category) {
      onError('Необходимо выбрать категорию');
      return;
    }

    setIsSubmitting(true);
    
    try {
      const formDataToSend = new FormData();
      
      // Добавляем все поля
      Object.entries(formData).forEach(([key, value]) => {
        if (value !== '' && value !== undefined) {
          formDataToSend.append(key, value.toString());
        }
      });
      
      // Добавляем файл, если есть
      if (selectedFile) {
        formDataToSend.append('image', selectedFile);
      }
      
      await dispatch(createDefect(formDataToSend)).unwrap();
      onSuccess('Дефект успешно создан');
      handleClose();
    } catch (error: any) {
      onError(error.message || 'Ошибка при создании дефекта');
    } finally {
      setIsSubmitting(false);
    }
  }, [formData, selectedFile, dispatch, onSuccess, onError, handleClose]);

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        component: 'form',
        onSubmit: handleSubmit
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          Создать новый дефект
          <IconButton onClick={handleClose} disabled={isSubmitting}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              label="Название дефекта"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              placeholder="Краткое описание проблемы..."
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              multiline
              rows={3}
              label="Описание"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Подробное описание дефекта..."
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl required fullWidth>
              <InputLabel>Проект</InputLabel>
              <Select
                value={formData.project}
                onChange={(e) => setFormData(prev => ({ ...prev, project: e.target.value as number }))}
                label="Проект"
              >
                {projects.map((project) => (
                  <MenuItem key={project.id} value={project.id}>
                    {project.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl required fullWidth>
              <InputLabel>Категория</InputLabel>
              <Select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as number }))}
                label="Категория"
              >
                {categories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: category.color
                        }}
                      />
                      {category.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Приоритет</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value }))}
                label="Приоритет"
              >
                {PRIORITY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Chip
                      label={option.label}
                      size="small"
                      sx={{
                        backgroundColor: option.color + '20',
                        color: option.color,
                        border: `1px solid ${option.color}30`
                      }}
                    />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Серьезность</InputLabel>
              <Select
                value={formData.severity}
                onChange={(e) => setFormData(prev => ({ ...prev, severity: e.target.value }))}
                label="Серьезность"
              >
                {SEVERITY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Chip
                      label={option.label}
                      size="small"
                      sx={{
                        backgroundColor: option.color + '20',
                        color: option.color,
                        border: `1px solid ${option.color}30`
                      }}
                    />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Исполнитель</InputLabel>
              <Select
                value={formData.assignee}
                onChange={(e) => setFormData(prev => ({ ...prev, assignee: e.target.value as number }))}
                label="Исполнитель"
              >
                <MenuItem value="">Не назначен</MenuItem>
                {engineers.map((engineer) => (
                  <MenuItem key={engineer.id} value={engineer.id}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Avatar sx={{ width: 20, height: 20, fontSize: '0.6rem' }}>
                        {engineer.first_name[0]}
                      </Avatar>
                      {engineer.first_name} {engineer.last_name}
                      <Typography variant="caption" color="text.secondary" ml={1}>
                        ({engineer.specialization})
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <TextField
              required
              fullWidth
              label="Местоположение"
              value={formData.location}
              onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
              placeholder="Здание, секция..."
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              label="Этаж"
              value={formData.floor}
              onChange={(e) => setFormData(prev => ({ ...prev, floor: e.target.value }))}
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              label="Помещение"
              value={formData.room}
              onChange={(e) => setFormData(prev => ({ ...prev, room: e.target.value }))}
            />
          </Grid>
          
          {formData.assignee && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Срок выполнения"
                value={formData.due_date}
                onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          )}
          
          {/* Загрузка файла */}
          <Grid item xs={12}>
            <Card variant="outlined">
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <ImageIcon color="action" />
                  <Typography variant="subtitle2">
                    Фотография дефекта
                  </Typography>
                </Box>
                
                {selectedFile ? (
                  <Box display="flex" alignItems="center" gap={2}>
                    <Typography variant="body2">
                      {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} МБ)
                    </Typography>
                    <IconButton 
                      size="small" 
                      onClick={() => setSelectedFile(null)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                ) : (
                  <Button
                    component="label"
                    variant="outlined"
                    startIcon={<UploadIcon />}
                  >
                    Выбрать файл
                    <input
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleFileSelect}
                    />
                  </Button>
                )}
                
                <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                  Поддерживаются изображения до 5МБ (JPG, PNG, GIF)
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={isSubmitting}>
          Отмена
        </Button>
        <Button 
          type="submit"
          variant="contained"
          disabled={isSubmitting}
          startIcon={<SendIcon />}
        >
          {isSubmitting ? 'Создание...' : 'Создать дефект'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Компонент изменения статуса
export const StatusChangeDialog: React.FC<StatusChangeDialogProps> = ({
  open,
  onClose,
  defect,
  onSuccess,
  onError
}) => {
  const dispatch = useAppDispatch();
  const [selectedStatus, setSelectedStatus] = useState('');
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (defect && open) {
      setSelectedStatus(defect.status);
      setComment('');
    }
  }, [defect, open]);

  const getValidNextStatuses = useCallback((currentStatus: string) => {
    const workflows: Record<string, string[]> = {
      'new': ['in_progress', 'cancelled'],
      'in_progress': ['review', 'cancelled'],
      'review': ['closed', 'in_progress'],
      'closed': [],
      'cancelled': ['new']
    };
    
    return workflows[currentStatus] || [];
  }, []);

  const getCurrentStepIndex = useCallback((status: string) => {
    return WORKFLOW_STEPS.findIndex(step => step.key === status);
  }, []);

  const handleSubmit = useCallback(async () => {
    if (!defect || !selectedStatus) return;
    
    if (selectedStatus === defect.status) {
      onError('Выберите новый статус');
      return;
    }

    setIsSubmitting(true);
    
    try {
      await dispatch(changeDefectStatus({
        id: defect.id,
        status: selectedStatus,
        comment: comment.trim() || undefined
      })).unwrap();
      
      onSuccess(`Статус дефекта изменен на "${STATUS_OPTIONS.find(s => s.value === selectedStatus)?.label}"`);
      onClose();
    } catch (error: any) {
      onError(error.message || 'Ошибка при изменении статуса');
    } finally {
      setIsSubmitting(false);
    }
  }, [defect, selectedStatus, comment, dispatch, onSuccess, onError, onClose]);

  if (!defect) return null;

  const validNextStatuses = getValidNextStatuses(defect.status);
  const currentStepIndex = getCurrentStepIndex(defect.status);
  const selectedStepIndex = getCurrentStepIndex(selectedStatus);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Изменить статус дефекта
        <Typography variant="body2" color="text.secondary" mt={1}>
          {defect.defect_number} - {defect.title}
        </Typography>
      </DialogTitle>
      
      <DialogContent dividers>
        <Box mb={3}>
          <Typography variant="subtitle2" gutterBottom>
            Текущий процесс:
          </Typography>
          <Stepper activeStep={currentStepIndex} alternativeLabel>
            {WORKFLOW_STEPS.map((step, index) => (
              <Step key={step.key} completed={index < currentStepIndex}>
                <StepLabel
                  sx={{
                    '& .MuiStepLabel-label': {
                      color: index === selectedStepIndex ? 'primary.main' : undefined
                    }
                  }}
                >
                  {step.label}
                </StepLabel>
              </Step>
            ))}
          </Stepper>
        </Box>

        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Новый статус</InputLabel>
          <Select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            label="Новый статус"
          >
            <MenuItem value={defect.status}>
              <Box display="flex" alignItems="center" gap={1}>
                <Chip
                  label={STATUS_OPTIONS.find(s => s.value === defect.status)?.label + ' (текущий)'}
                  size="small"
                  disabled
                />
              </Box>
            </MenuItem>
            {validNextStatuses.map((status) => {
              const statusOption = STATUS_OPTIONS.find(s => s.value === status);
              return (
                <MenuItem key={status} value={status}>
                  <Chip
                    label={statusOption?.label}
                    size="small"
                    sx={{
                      backgroundColor: statusOption?.color,
                      color: 'white'
                    }}
                  />
                </MenuItem>
              );
            })}
          </Select>
        </FormControl>

        <TextField
          fullWidth
          multiline
          rows={3}
          label="Комментарий"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Опишите причину изменения статуса..."
        />

        {selectedStatus && selectedStatus !== defect.status && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Статус будет изменен с "{STATUS_OPTIONS.find(s => s.value === defect.status)?.label}" 
            на "{STATUS_OPTIONS.find(s => s.value === selectedStatus)?.label}"
          </Alert>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>
          Отмена
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isSubmitting || selectedStatus === defect.status}
        >
          {isSubmitting ? 'Изменение...' : 'Изменить статус'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Компонент назначения исполнителя
export const AssignDefectDialog: React.FC<AssignDefectDialogProps> = ({
  open,
  onClose,
  defect,
  engineers,
  onSuccess,
  onError
}) => {
  const dispatch = useAppDispatch();
  const [selectedEngineer, setSelectedEngineer] = useState<number | ''>('');
  const [dueDate, setDueDate] = useState('');
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (defect && open) {
      setSelectedEngineer(defect.assignee?.id || '');
      setDueDate(defect.due_date || '');
      setComment('');
    }
  }, [defect, open]);

  const handleSubmit = useCallback(async () => {
    if (!defect || !selectedEngineer) {
      onError('Выберите исполнителя');
      return;
    }

    setIsSubmitting(true);
    
    try {
      await dispatch(assignDefect({
        id: defect.id,
        assignee: selectedEngineer as number,
        due_date: dueDate || undefined,
        comment: comment.trim() || undefined
      })).unwrap();
      
      const engineerName = engineers.find(e => e.id === selectedEngineer);
      onSuccess(`Дефект назначен исполнителю: ${engineerName?.first_name} ${engineerName?.last_name}`);
      onClose();
    } catch (error: any) {
      onError(error.message || 'Ошибка при назначении исполнителя');
    } finally {
      setIsSubmitting(false);
    }
  }, [defect, selectedEngineer, dueDate, comment, dispatch, engineers, onSuccess, onError, onClose]);

  if (!defect) return null;

  const selectedEngineerData = engineers.find(e => e.id === selectedEngineer);

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        Назначить исполнителя
        <Typography variant="body2" color="text.secondary" mt={1}>
          {defect.defect_number} - {defect.title}
        </Typography>
      </DialogTitle>
      
      <DialogContent dividers>
        {defect.assignee && (
          <Alert severity="info" sx={{ mb: 2 }}>
            Текущий исполнитель: {defect.assignee.first_name} {defect.assignee.last_name}
          </Alert>
        )}

        <FormControl fullWidth sx={{ mb: 3 }}>
          <InputLabel>Исполнитель</InputLabel>
          <Select
            value={selectedEngineer}
            onChange={(e) => setSelectedEngineer(e.target.value as number)}
            label="Исполнитель"
          >
            <MenuItem value="">Не назначен</MenuItem>
            {engineers.map((engineer) => (
              <MenuItem key={engineer.id} value={engineer.id}>
                <Box display="flex" alignItems="center" gap={1} width="100%">
                  <Avatar sx={{ width: 28, height: 28, fontSize: '0.75rem' }}>
                    {engineer.first_name[0]}
                  </Avatar>
                  <Box>
                    <Typography variant="body2">
                      {engineer.first_name} {engineer.last_name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {engineer.specialization}
                    </Typography>
                  </Box>
                </Box>
              </MenuItem>
            ))}
          </Select>
        </FormControl>

        {selectedEngineerData && (
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar>
                  {selectedEngineerData.first_name[0]}
                </Avatar>
                <Box>
                  <Typography variant="subtitle1">
                    {selectedEngineerData.first_name} {selectedEngineerData.last_name}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Специализация: {selectedEngineerData.specialization}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        )}

        <TextField
          fullWidth
          type="date"
          label="Срок выполнения"
          value={dueDate}
          onChange={(e) => setDueDate(e.target.value)}
          InputLabelProps={{ shrink: true }}
          sx={{ mb: 3 }}
        />

        <TextField
          fullWidth
          multiline
          rows={3}
          label="Комментарий"
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Дополнительные указания для исполнителя..."
        />
      </DialogContent>
      
      <DialogActions>
        <Button onClick={onClose} disabled={isSubmitting}>
          Отмена
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={isSubmitting || !selectedEngineer}
        >
          {isSubmitting ? 'Назначение...' : 'Назначить исполнителя'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

// Компонент редактирования дефекта
export const EditDefectDialog: React.FC<EditDefectDialogProps> = ({
  open,
  onClose,
  defect,
  projects,
  categories,
  engineers,
  onSuccess,
  onError
}) => {
  const dispatch = useAppDispatch();
  const [formData, setFormData] = useState<DefectFormData>({
    title: '',
    description: '',
    priority: 'medium',
    severity: 'minor',
    project: '',
    category: '',
    location: '',
    floor: '',
    room: '',
    assignee: '',
    due_date: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (defect && open) {
      setFormData({
        title: defect.title,
        description: defect.description,
        priority: defect.priority,
        severity: defect.severity,
        project: defect.project.id,
        category: defect.category.id,
        location: defect.location,
        floor: defect.floor || '',
        room: defect.room || '',
        assignee: defect.assignee?.id || '',
        due_date: defect.due_date || ''
      });
    }
  }, [defect, open]);

  const handleClose = useCallback(() => {
    if (!isSubmitting) {
      onClose();
    }
  }, [isSubmitting, onClose]);

  const handleSubmit = useCallback(async (event: React.FormEvent) => {
    event.preventDefault();
    
    if (!defect || !formData.title.trim()) {
      onError('Необходимо указать название дефекта');
      return;
    }

    setIsSubmitting(true);
    
    try {
      await dispatch(updateDefect({
        id: defect.id,
        data: {
          title: formData.title,
          description: formData.description,
          priority: formData.priority as any,
          severity: formData.severity as any,
          project: { id: formData.project as number, name: '' },
          category: { id: formData.category as number, name: '', color: '' },
          location: formData.location,
          floor: formData.floor || undefined,
          room: formData.room || undefined,
          due_date: formData.due_date || undefined
        }
      })).unwrap();
      
      onSuccess('Дефект успешно обновлен');
      handleClose();
    } catch (error: any) {
      onError(error.message || 'Ошибка при обновлении дефекта');
    } finally {
      setIsSubmitting(false);
    }
  }, [defect, formData, dispatch, onSuccess, onError, handleClose]);

  if (!defect) return null;

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        component: 'form',
        onSubmit: handleSubmit
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          Редактировать дефект
          <IconButton onClick={handleClose} disabled={isSubmitting}>
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              label="Название дефекта"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
            />
          </Grid>
          
          <Grid item xs={12}>
            <TextField
              required
              fullWidth
              multiline
              rows={3}
              label="Описание"
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
            />
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl required fullWidth>
              <InputLabel>Проект</InputLabel>
              <Select
                value={formData.project}
                onChange={(e) => setFormData(prev => ({ ...prev, project: e.target.value as number }))}
                label="Проект"
              >
                {projects.map((project) => (
                  <MenuItem key={project.id} value={project.id}>
                    {project.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={6}>
            <FormControl required fullWidth>
              <InputLabel>Категория</InputLabel>
              <Select
                value={formData.category}
                onChange={(e) => setFormData(prev => ({ ...prev, category: e.target.value as number }))}
                label="Категория"
              >
                {categories.map((category) => (
                  <MenuItem key={category.id} value={category.id}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Box
                        sx={{
                          width: 12,
                          height: 12,
                          borderRadius: '50%',
                          backgroundColor: category.color
                        }}
                      />
                      {category.name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Приоритет</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value }))}
                label="Приоритет"
              >
                {PRIORITY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Chip
                      label={option.label}
                      size="small"
                      sx={{
                        backgroundColor: option.color + '20',
                        color: option.color,
                        border: `1px solid ${option.color}30`
                      }}
                    />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Серьезность</InputLabel>
              <Select
                value={formData.severity}
                onChange={(e) => setFormData(prev => ({ ...prev, severity: e.target.value }))}
                label="Серьезность"
              >
                {SEVERITY_OPTIONS.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Chip
                      label={option.label}
                      size="small"
                      sx={{
                        backgroundColor: option.color + '20',
                        color: option.color,
                        border: `1px solid ${option.color}30`
                      }}
                    />
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Исполнитель</InputLabel>
              <Select
                value={formData.assignee}
                onChange={(e) => setFormData(prev => ({ ...prev, assignee: e.target.value as number }))}
                label="Исполнитель"
              >
                <MenuItem value="">Не назначен</MenuItem>
                {engineers.map((engineer) => (
                  <MenuItem key={engineer.id} value={engineer.id}>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Avatar sx={{ width: 20, height: 20, fontSize: '0.6rem' }}>
                        {engineer.first_name[0]}
                      </Avatar>
                      {engineer.first_name} {engineer.last_name}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={8}>
            <TextField
              required
              fullWidth
              label="Местоположение"
              value={formData.location}
              onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              label="Этаж"
              value={formData.floor}
              onChange={(e) => setFormData(prev => ({ ...prev, floor: e.target.value }))}
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <TextField
              fullWidth
              label="Помещение"
              value={formData.room}
              onChange={(e) => setFormData(prev => ({ ...prev, room: e.target.value }))}
            />
          </Grid>
          
          {formData.assignee && (
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                type="date"
                label="Срок выполнения"
                value={formData.due_date}
                onChange={(e) => setFormData(prev => ({ ...prev, due_date: e.target.value }))}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
          )}
        </Grid>
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} disabled={isSubmitting}>
          Отмена
        </Button>
        <Button 
          type="submit"
          variant="contained"
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Сохранение...' : 'Сохранить изменения'}
        </Button>
      </DialogActions>
    </Dialog>
  );
};