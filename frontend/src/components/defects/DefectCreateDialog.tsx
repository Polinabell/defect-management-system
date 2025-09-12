/**
 * Диалог создания нового дефекта
 */

import React, { useState, useEffect } from 'react';
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
  Box,
  Typography,
  Chip,
  IconButton,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Alert,
  Autocomplete,
  Divider
} from '@mui/material';
import {
  CloudUpload as CloudUploadIcon,
  Delete as DeleteIcon,
  InsertDriveFile as FileIcon,
  Image as ImageIcon,
  Description as DescriptionIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import { useAppSelector } from '../../store/index';
import { selectProjectsList } from '../../store/slices/projectsSlice';

interface DefectCreateDialogProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (defectData: any, files: File[]) => Promise<void>;
  projects: any[];
  users: any[];
}

interface DefectFormData {
  title: string;
  description: string;
  project: number | null;
  category: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  severity: 'minor' | 'major' | 'critical' | 'blocker';
  assignee: number | null;
  due_date: string;
  location: string;
  environment: string;
}

const priorityOptions = [
  { value: 'low', label: 'Низкий', color: '#4caf50' },
  { value: 'medium', label: 'Средний', color: '#ff9800' },
  { value: 'high', label: 'Высокий', color: '#f44336' },
  { value: 'critical', label: 'Критический', color: '#d32f2f' }
];

const severityOptions = [
  { value: 'minor', label: 'Незначительный', color: '#4caf50' },
  { value: 'major', label: 'Значительный', color: '#ff9800' },
  { value: 'critical', label: 'Критический', color: '#f44336' },
  { value: 'blocker', label: 'Блокирующий', color: '#d32f2f' }
];

const categoryOptions = [
  'Конструкция',
  'Отделка',
  'Инженерные системы',
  'Благоустройство',
  'Безопасность',
  'Документация',
  'Другое'
];

export const DefectCreateDialog: React.FC<DefectCreateDialogProps> = ({
  open,
  onClose,
  onSubmit,
  projects,
  users
}) => {
  const [formData, setFormData] = useState<DefectFormData>({
    title: '',
    description: '',
    project: null,
    category: '',
    priority: 'medium',
    severity: 'major',
    assignee: null,
    due_date: '',
    location: '',
    environment: ''
  });

  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.gif', '.webp'],
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
      'text/plain': ['.txt'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    maxFiles: 10,
    maxSize: 10 * 1024 * 1024, // 10MB
    onDrop: (acceptedFiles) => {
      setFiles(prev => [...prev, ...acceptedFiles]);
    },
    onDropRejected: (rejectedFiles) => {
      rejectedFiles.forEach(file => {
        file.errors.forEach(error => {
          if (error.code === 'file-too-large') {
            setErrors(prev => ({ ...prev, files: 'Файл слишком большой (максимум 10MB)' }));
          } else if (error.code === 'file-invalid-type') {
            setErrors(prev => ({ ...prev, files: 'Неподдерживаемый тип файла' }));
          }
        });
      });
    }
  });

  const handleInputChange = (field: keyof DefectFormData, value: any) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Убираем ошибку для поля при изменении
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const removeFile = (index: number) => {
    setFiles(prev => prev.filter((_, i) => i !== index));
  };

  const validateForm = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Название обязательно';
    }
    if (!formData.description.trim()) {
      newErrors.description = 'Описание обязательно';
    }
    if (!formData.project) {
      newErrors.project = 'Выберите проект';
    }
    if (!formData.category) {
      newErrors.category = 'Выберите категорию';
    }
    if (formData.due_date && new Date(formData.due_date) <= new Date()) {
      newErrors.due_date = 'Срок выполнения должен быть в будущем';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async () => {
    if (!validateForm()) return;

    setUploading(true);
    try {
      await onSubmit(formData, files);
      handleClose();
    } catch (error) {
      console.error('Ошибка создания дефекта:', error);
    } finally {
      setUploading(false);
    }
  };

  const handleClose = () => {
    setFormData({
      title: '',
      description: '',
      project: null,
      category: '',
      priority: 'medium',
      severity: 'major',
      assignee: null,
      due_date: '',
      location: '',
      environment: ''
    });
    setFiles([]);
    setErrors({});
    setUploading(false);
    onClose();
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) {
      return <ImageIcon color="primary" />;
    } else if (file.type === 'application/pdf') {
      return <DescriptionIcon color="error" />;
    } else {
      return <FileIcon color="action" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <Dialog 
      open={open} 
      onClose={handleClose}
      maxWidth="md"
      fullWidth
      PaperProps={{
        sx: { minHeight: '80vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6" fontWeight="bold">
            Создать новый дефект
          </Typography>
          <IconButton onClick={handleClose} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>

      <DialogContent dividers>
        <Grid container spacing={3}>
          {/* Основная информация */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Основная информация
            </Typography>
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Название дефекта"
              value={formData.title}
              onChange={(e) => handleInputChange('title', e.target.value)}
              fullWidth
              required
              error={!!errors.title}
              helperText={errors.title}
              placeholder="Краткое описание проблемы"
            />
          </Grid>

          <Grid item xs={12}>
            <TextField
              label="Описание"
              value={formData.description}
              onChange={(e) => handleInputChange('description', e.target.value)}
              fullWidth
              required
              multiline
              rows={4}
              error={!!errors.description}
              helperText={errors.description}
              placeholder="Подробное описание дефекта, включая шаги воспроизведения и ожидаемый результат"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required error={!!errors.project}>
              <InputLabel>Проект</InputLabel>
              <Select
                value={formData.project || ''}
                onChange={(e) => handleInputChange('project', e.target.value)}
                label="Проект"
              >
                {projects.map((project) => (
                  <MenuItem key={project.id} value={project.id}>
                    {project.name}
                  </MenuItem>
                ))}
              </Select>
              {errors.project && (
                <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                  {errors.project}
                </Typography>
              )}
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth required error={!!errors.category}>
              <InputLabel>Категория</InputLabel>
              <Select
                value={formData.category}
                onChange={(e) => handleInputChange('category', e.target.value)}
                label="Категория"
              >
                {categoryOptions.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
              {errors.category && (
                <Typography variant="caption" color="error" sx={{ mt: 1, ml: 2 }}>
                  {errors.category}
                </Typography>
              )}
            </FormControl>
          </Grid>

          {/* Приоритет и серьезность */}
          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Приоритет</InputLabel>
              <Select
                value={formData.priority}
                onChange={(e) => handleInputChange('priority', e.target.value)}
                label="Приоритет"
              >
                {priorityOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Box display="flex" alignItems="center">
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={option.color}
                        mr={1}
                      />
                      {option.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6}>
            <FormControl fullWidth>
              <InputLabel>Серьезность</InputLabel>
              <Select
                value={formData.severity}
                onChange={(e) => handleInputChange('severity', e.target.value)}
                label="Серьезность"
              >
                {severityOptions.map((option) => (
                  <MenuItem key={option.value} value={option.value}>
                    <Box display="flex" alignItems="center">
                      <Box
                        width={12}
                        height={12}
                        borderRadius="50%"
                        bgcolor={option.color}
                        mr={1}
                      />
                      {option.label}
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Назначение и сроки */}
          <Grid item xs={12} sm={6}>
            <Autocomplete
              options={users}
              getOptionLabel={(user) => `${user.first_name} ${user.last_name} (${user.username})`}
              value={users.find(u => u.id === formData.assignee) || null}
              onChange={(_, user) => handleInputChange('assignee', user?.id || null)}
              renderInput={(params) => (
                <TextField {...params} label="Исполнитель" placeholder="Выберите исполнителя" />
              )}
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              label="Срок выполнения"
              type="datetime-local"
              value={formData.due_date}
              onChange={(e) => handleInputChange('due_date', e.target.value)}
              fullWidth
              InputLabelProps={{ shrink: true }}
              error={!!errors.due_date}
              helperText={errors.due_date}
            />
          </Grid>

          {/* Дополнительная информация */}
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Дополнительная информация
            </Typography>
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              label="Местоположение"
              value={formData.location}
              onChange={(e) => handleInputChange('location', e.target.value)}
              fullWidth
              placeholder="Здание, этаж, помещение"
            />
          </Grid>

          <Grid item xs={12} sm={6}>
            <TextField
              label="Окружение"
              value={formData.environment}
              onChange={(e) => handleInputChange('environment', e.target.value)}
              fullWidth
              placeholder="Условия, при которых обнаружен дефект"
            />
          </Grid>

          {/* Загрузка файлов */}
          <Grid item xs={12}>
            <Divider sx={{ my: 2 }} />
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Вложения
            </Typography>
            
            <Card
              {...getRootProps()}
              sx={{
                border: '2px dashed',
                borderColor: isDragActive ? 'primary.main' : 'grey.300',
                backgroundColor: isDragActive ? 'action.hover' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                '&:hover': {
                  borderColor: 'primary.main',
                  backgroundColor: 'action.hover'
                }
              }}
            >
              <input {...getInputProps()} />
              <CardContent sx={{ textAlign: 'center', py: 4 }}>
                <CloudUploadIcon sx={{ fontSize: 48, color: 'grey.400', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Отпустите файлы здесь' : 'Перетащите файлы сюда'}
                </Typography>
                <Typography variant="body2" color="text.secondary" gutterBottom>
                  или нажмите для выбора файлов
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Поддерживаются: изображения, PDF, DOC, XLS (до 10MB каждый)
                </Typography>
              </CardContent>
            </Card>

            {errors.files && (
              <Alert severity="error" sx={{ mt: 2 }}>
                {errors.files}
              </Alert>
            )}

            {/* Список загруженных файлов */}
            {files.length > 0 && (
              <Box mt={2}>
                <Typography variant="subtitle2" gutterBottom>
                  Выбранные файлы ({files.length}):
                </Typography>
                {files.map((file, index) => (
                  <Box
                    key={index}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    p={1}
                    border={1}
                    borderColor="grey.300"
                    borderRadius={1}
                    mb={1}
                  >
                    <Box display="flex" alignItems="center">
                      {getFileIcon(file)}
                      <Box ml={1}>
                        <Typography variant="body2" noWrap>
                          {file.name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatFileSize(file.size)}
                        </Typography>
                      </Box>
                    </Box>
                    <IconButton size="small" onClick={() => removeFile(index)}>
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                ))}
              </Box>
            )}
          </Grid>
        </Grid>
      </DialogContent>

      <DialogActions sx={{ p: 3 }}>
        <Button onClick={handleClose} disabled={uploading}>
          Отмена
        </Button>
        <Button
          onClick={handleSubmit}
          variant="contained"
          disabled={uploading}
          startIcon={uploading ? undefined : <CloudUploadIcon />}
        >
          {uploading ? 'Создание...' : 'Создать дефект'}
        </Button>
      </DialogActions>

      {uploading && <LinearProgress />}
    </Dialog>
  );
};
