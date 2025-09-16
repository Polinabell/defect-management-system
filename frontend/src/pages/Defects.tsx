/**
 * Страница дефектов
 */

import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  Box,
  Typography,
  Button,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Menu,
  MenuItem,
  TextField,
  FormControl,
  InputLabel,
  Select,
  OutlinedInput,
  Grid,
  Card,
  CardContent,
  Avatar,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Alert,
  Snackbar,
  Stack,
  Autocomplete,
  LinearProgress,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assignment as AssignIcon,
  ChangeCircle as StatusIcon,
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  Image as ImageIcon,
  Person as PersonIcon,
  CalendarToday as CalendarIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Cancel as CancelIcon,
  Visibility as ViewIcon,
  ContentCopy as CopyIcon,
  FileDownload as ExportIcon,
  Comment as CommentIcon,
  History as HistoryIcon,
  Share as ShareIcon,
  Print as PrintIcon,
  AttachFile as AttachFileIcon
} from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../store/index';
import {
  fetchDefects,
  createDefect,
  updateDefect,
  changeDefectStatus,
  assignDefect,
  setFilters,
  clearFilters,
  setPage,
  setPageSize,
  clearError,
  selectDefectsList,
  selectDefectsLoading,
  selectDefectsError,
  selectDefectsFilters,
  Defect
} from '../store/slices/defectsSlice';
import { fetchProjects, selectProjectsList } from '../store/slices/projectsSlice';
import { defectsAPI } from '../services/api';
import { RoleGuard, usePermissions, PERMISSIONS } from '../components/common/RoleGuard';
import { DefectCreateDialog } from '../components/defects/DefectCreateDialog';

// Константы для статусов, приоритетов и серьезности
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

// Компонент фильтров
const DefectsFilters: React.FC<{
  filters: any;
  onFiltersChange: (filters: any) => void;
  onClearFilters: () => void;
  projects: any[];
  categories: any[];
  engineers: any[];
}> = ({ filters, onFiltersChange, onClearFilters, projects, categories, engineers }) => {
  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <FilterIcon />
          Фильтры
        </Typography>
        <Button 
          startIcon={<ClearIcon />} 
          onClick={onClearFilters}
          size="small"
        >
          Очистить
        </Button>
      </Box>
      
      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Поиск"
            value={filters.search || ''}
            onChange={(e) => onFiltersChange({ ...filters, search: e.target.value })}
            InputProps={{
              startAdornment: <SearchIcon sx={{ mr: 1, color: 'action.active' }} />
            }}
            placeholder="Номер, название, описание..."
          />
        </Grid>
        
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>Статус</InputLabel>
            <Select
              multiple
              value={filters.status || []}
              onChange={(e) => onFiltersChange({ ...filters, status: e.target.value })}
              input={<OutlinedInput label="Статус" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {(selected as string[]).map((value) => (
                    <Chip
                      key={value}
                      label={STATUS_OPTIONS.find(s => s.value === value)?.label}
                      size="small"
                    />
                  ))}
                </Box>
              )}
            >
              {STATUS_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>Приоритет</InputLabel>
            <Select
              multiple
              value={filters.priority || []}
              onChange={(e) => onFiltersChange({ ...filters, priority: e.target.value })}
              input={<OutlinedInput label="Приоритет" />}
              renderValue={(selected) => (
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {(selected as string[]).map((value) => (
                    <Chip
                      key={value}
                      label={PRIORITY_OPTIONS.find(p => p.value === value)?.label}
                      size="small"
                    />
                  ))}
                </Box>
              )}
            >
              {PRIORITY_OPTIONS.map((option) => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>Проект</InputLabel>
            <Select
              value={filters.project || ''}
              onChange={(e) => onFiltersChange({ ...filters, project: e.target.value })}
              label="Проект"
            >
              <MenuItem value="">Все проекты</MenuItem>
              {projects.map((project) => (
                <MenuItem key={project.id} value={project.id}>
                  {project.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>Исполнитель</InputLabel>
            <Select
              value={filters.assignee || ''}
              onChange={(e) => onFiltersChange({ ...filters, assignee: e.target.value })}
              label="Исполнитель"
            >
              <MenuItem value="">Все исполнители</MenuItem>
              {engineers.map((engineer) => (
                <MenuItem key={engineer.id} value={engineer.id}>
                  {engineer.first_name} {engineer.last_name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>
    </Paper>
  );
};

export const Defects: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const defects = useAppSelector(selectDefectsList) as Defect[];
  const isLoading = useAppSelector(selectDefectsLoading);
  const error = useAppSelector(selectDefectsError);
  const filters = useAppSelector(selectDefectsFilters);

  // Заглушки для пагинации (можно добавить позже)
  const totalCount = defects.length;
  const page = 1;
  const pageSize = 10;
  const projects = useAppSelector(selectProjectsList);

  // Хук для проверки прав доступа
  const permissions = usePermissions();
  
  // Локальное состояние
  const [categories, setCategories] = useState<any[]>([]);
  const [engineers, setEngineers] = useState<any[]>([]);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [statusDialogOpen, setStatusDialogOpen] = useState(false);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [snackbarMessage, setSnackbarMessage] = useState('');
  const [snackbarSeverity, setSnackbarSeverity] = useState<'success' | 'error'>('success');
  
  // Загрузка данных
  useEffect(() => {
    dispatch(fetchDefects({ page, pageSize, ...filters }) as any);
    dispatch(fetchProjects({}) as any);
    
    // Загрузка категорий и инженеров
    Promise.all([
      defectsAPI.getCategories(),
      defectsAPI.getEngineers()
    ]).then(([categoriesData, engineersData]) => {
      setCategories(categoriesData);
      setEngineers(engineersData);
    });
  }, [dispatch, page, pageSize, filters]);

  // Проверка URL параметра для автоматического открытия диалога создания
  useEffect(() => {
    const shouldCreate = searchParams.get('create');
    if (shouldCreate === 'true') {
      setCreateDialogOpen(true);
      // Убираем параметр из URL после открытия диалога
      searchParams.delete('create');
      setSearchParams(searchParams, { replace: true });
    }
  }, [searchParams, setSearchParams]);

  // Обработчики событий
  const handleFiltersChange = useCallback((newFilters: any) => {
    dispatch(setFilters(newFilters));
    dispatch(setPage(1)); // Сброс на первую страницу при изменении фильтров
  }, [dispatch]);
  
  const handleClearFilters = useCallback(() => {
    dispatch(clearFilters());
    dispatch(setPage(1));
  }, [dispatch]);
  
  const handlePageChange = useCallback((event: unknown, newPage: number) => {
    dispatch(setPage(newPage + 1));
  }, [dispatch]);
  
  const handlePageSizeChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    dispatch(setPageSize(parseInt(event.target.value, 10)));
    dispatch(setPage(1));
  }, [dispatch]);
  
  const handleMenuOpen = useCallback((event: React.MouseEvent<HTMLElement>, defect: Defect) => {
    console.log('Defects: Открытие меню для дефекта', defect.id, defect.title);
    console.log('Defects: Разрешения пользователя:', {
      canEdit: permissions.canEdit(),
      canChangeStatus: permissions.canChangeStatus(),
      canAssign: permissions.canAssign(),
      canDelete: permissions.canDelete()
    });
    setMenuAnchor(event.currentTarget);
    setSelectedDefect(defect);
  }, [permissions]);
  
  const handleMenuClose = useCallback(() => {
    setMenuAnchor(null);
    setSelectedDefect(null);
  }, []);
  
  const handleEdit = useCallback(() => {
    setEditDialogOpen(true);
    handleMenuClose();
  }, [handleMenuClose]);
  
  const handleStatusChange = useCallback(() => {
    setStatusDialogOpen(true);
    handleMenuClose();
  }, [handleMenuClose]);
  
  const handleAssign = useCallback(() => {
    setAssignDialogOpen(true);
    handleMenuClose();
  }, [handleMenuClose]);
  
  const showSnackbar = useCallback((message: string, severity: 'success' | 'error' = 'success') => {
    setSnackbarMessage(message);
    setSnackbarSeverity(severity);
    setSnackbarOpen(true);
  }, []);

  const handleCreateDefect = useCallback(async (defectData: any, files: File[]) => {
    try {
      await dispatch(createDefect(defectData) as any);
      showSnackbar('Дефект успешно создан');
      setCreateDialogOpen(false);
    } catch (error) {
      showSnackbar('Ошибка создания дефекта', 'error');
      throw error;
    }
  }, [dispatch, showSnackbar]);

  // Дополнительные обработчики действий
  const handleCopyDefect = useCallback(() => {
    if (selectedDefect) {
      const defectInfo = `
Дефект: ${selectedDefect.title}
Номер: ${selectedDefect.defect_number}
Проект: ${selectedDefect.project.name}
Статус: ${selectedDefect.status}
Приоритет: ${selectedDefect.priority}
Описание: ${selectedDefect.description}
Местоположение: ${selectedDefect.location}
      `.trim();

      navigator.clipboard.writeText(defectInfo).then(() => {
        showSnackbar('Информация о дефекте скопирована в буфер обмена');
      }).catch(() => {
        showSnackbar('Ошибка копирования', 'error');
      });
    }
    handleMenuClose();
  }, [selectedDefect, showSnackbar, handleMenuClose]);

  const handleExportDefect = useCallback(() => {
    if (selectedDefect) {
      const defectData = {
        title: selectedDefect.title,
        number: selectedDefect.defect_number,
        project: selectedDefect.project.name,
        status: selectedDefect.status,
        priority: selectedDefect.priority,
        severity: selectedDefect.severity,
        description: selectedDefect.description,
        location: selectedDefect.location,
        created_at: selectedDefect.created_at,
        author: `${selectedDefect.author.first_name} ${selectedDefect.author.last_name}`,
        assignee: selectedDefect.assignee ? `${selectedDefect.assignee.first_name} ${selectedDefect.assignee.last_name}` : 'Не назначен'
      };

      const dataStr = JSON.stringify(defectData, null, 2);
      const dataBlob = new Blob([dataStr], { type: 'application/json' });
      const url = URL.createObjectURL(dataBlob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `defect-${selectedDefect.defect_number}.json`;
      link.click();
      URL.revokeObjectURL(url);

      showSnackbar('Дефект экспортирован');
    }
    handleMenuClose();
  }, [selectedDefect, showSnackbar, handleMenuClose]);

  const handlePrintDefect = useCallback(() => {
    if (selectedDefect) {
      const printWindow = window.open('', '_blank');
      if (printWindow) {
        printWindow.document.write(`
          <html>
            <head>
              <title>Дефект ${selectedDefect.defect_number}</title>
              <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .header { border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-bottom: 20px; }
                .field { margin-bottom: 10px; }
                .label { font-weight: bold; }
              </style>
            </head>
            <body>
              <div class="header">
                <h1>Дефект ${selectedDefect.defect_number}</h1>
                <h2>${selectedDefect.title}</h2>
              </div>
              <div class="field"><span class="label">Проект:</span> ${selectedDefect.project.name}</div>
              <div class="field"><span class="label">Статус:</span> ${selectedDefect.status}</div>
              <div class="field"><span class="label">Приоритет:</span> ${selectedDefect.priority}</div>
              <div class="field"><span class="label">Серьезность:</span> ${selectedDefect.severity}</div>
              <div class="field"><span class="label">Местоположение:</span> ${selectedDefect.location}</div>
              <div class="field"><span class="label">Автор:</span> ${selectedDefect.author.first_name} ${selectedDefect.author.last_name}</div>
              <div class="field"><span class="label">Исполнитель:</span> ${selectedDefect.assignee ? `${selectedDefect.assignee.first_name} ${selectedDefect.assignee.last_name}` : 'Не назначен'}</div>
              <div class="field"><span class="label">Создан:</span> ${new Date(selectedDefect.created_at).toLocaleDateString('ru-RU')}</div>
              <div class="field">
                <div class="label">Описание:</div>
                <p>${selectedDefect.description}</p>
              </div>
            </body>
          </html>
        `);
        printWindow.document.close();
        printWindow.print();
        showSnackbar('Отправлено на печать');
      }
    }
    handleMenuClose();
  }, [selectedDefect, showSnackbar, handleMenuClose]);

  const handleShareDefect = useCallback(() => {
    if (selectedDefect) {
      const shareUrl = `${window.location.origin}/defects/${selectedDefect.id}`;

      if (navigator.share) {
        navigator.share({
          title: `Дефект ${selectedDefect.defect_number}`,
          text: selectedDefect.title,
          url: shareUrl
        }).then(() => {
          showSnackbar('Ссылка поделена');
        }).catch(() => {
          // Fallback to clipboard
          navigator.clipboard.writeText(shareUrl);
          showSnackbar('Ссылка скопирована в буфер обмена');
        });
      } else {
        navigator.clipboard.writeText(shareUrl);
        showSnackbar('Ссылка скопирована в буфер обмена');
      }
    }
    handleMenuClose();
  }, [selectedDefect, showSnackbar, handleMenuClose]);

  const handleAddComment = useCallback(() => {
    if (selectedDefect) {
      navigate(`/defects/${selectedDefect.id}?tab=comments`);
    }
    handleMenuClose();
  }, [selectedDefect, navigate, handleMenuClose]);

  const handleViewHistory = useCallback(() => {
    if (selectedDefect) {
      navigate(`/defects/${selectedDefect.id}?tab=history`);
    }
    handleMenuClose();
  }, [selectedDefect, navigate, handleMenuClose]);
  
  const getStatusChip = (status: string) => {
    const statusOption = STATUS_OPTIONS.find(s => s.value === status);
    const StatusIcon = status === 'new' ? ScheduleIcon : 
                      status === 'in_progress' ? ScheduleIcon :
                      status === 'review' ? WarningIcon :
                      status === 'closed' ? CheckCircleIcon : CancelIcon;
    
    return (
      <Chip
        icon={<StatusIcon />}
        label={statusOption?.label || status}
        size="small"
        sx={{
          backgroundColor: statusOption?.color || '#gray',
          color: 'white',
          '& .MuiChip-icon': { color: 'white' }
        }}
      />
    );
  };
  
  const getPriorityChip = (priority: string) => {
    const priorityOption = PRIORITY_OPTIONS.find(p => p.value === priority);
    return (
      <Chip
        label={priorityOption?.label || priority}
        size="small"
        variant="outlined"
        sx={{
          borderColor: priorityOption?.color || '#gray',
          color: priorityOption?.color || '#gray'
        }}
      />
    );
  };
  
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };
  
  const getDaysRemainingChip = (defect: Defect) => {
    if (!defect.due_date) return null;
    
    const isOverdue = defect.is_overdue;
    const daysRemaining = defect.days_remaining || 0;
    
    return (
      <Chip
        icon={isOverdue ? <WarningIcon /> : <CalendarIcon />}
        label={isOverdue ? `Просрочено на ${Math.abs(daysRemaining)} дн.` : `${daysRemaining} дн.`}
        size="small"
        color={isOverdue ? 'error' : daysRemaining <= 3 ? 'warning' : 'default'}
        variant={isOverdue ? 'filled' : 'outlined'}
      />
    );
  };

  return (
    <Box>
      {/* Заголовок */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Дефекты
        </Typography>
        <RoleGuard permission={PERMISSIONS.CREATE_DEFECT}>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            Добавить дефект
          </Button>
        </RoleGuard>
      </Box>
      
      {/* Статистика */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'primary.main' }}>
                  <ScheduleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{defects.filter(d => d.status === 'new').length}</Typography>
                  <Typography variant="body2" color="text.secondary">Новые</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'warning.main' }}>
                  <ScheduleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{defects.filter(d => d.status === 'in_progress').length}</Typography>
                  <Typography variant="body2" color="text.secondary">В работе</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'error.main' }}>
                  <WarningIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{defects.filter(d => d.is_overdue).length}</Typography>
                  <Typography variant="body2" color="text.secondary">Просрочено</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar sx={{ bgcolor: 'success.main' }}>
                  <CheckCircleIcon />
                </Avatar>
                <Box>
                  <Typography variant="h6">{defects.filter(d => d.status === 'closed').length}</Typography>
                  <Typography variant="body2" color="text.secondary">Закрыто</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      
      {/* Фильтры */}
      <DefectsFilters
        filters={filters}
        onFiltersChange={handleFiltersChange}
        onClearFilters={handleClearFilters}
        projects={projects}
        categories={categories}
        engineers={engineers}
      />
      
      {/* Таблица дефектов */}
      <Paper>
        {isLoading && <LinearProgress />}
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>№</TableCell>
                <TableCell>Название</TableCell>
                <TableCell>Проект</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Приоритет</TableCell>
                <TableCell>Исполнитель</TableCell>
                <TableCell>Срок</TableCell>
                <TableCell>Создан</TableCell>
                <TableCell align="center">Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {defects.map((defect) => (
                <TableRow 
                  key={defect.id} 
                  hover 
                  sx={{ cursor: 'pointer' }}
                  onClick={() => navigate(`/defects/${defect.id}`)}
                >
                  <TableCell>
                    <Box display="flex" alignItems="center" gap={1}>
                      <Typography variant="body2" fontWeight="medium">
                        {defect.defect_number}
                      </Typography>
                      {defect.main_image && (
                        <Tooltip title="Есть фото">
                          <ImageIcon color="action" fontSize="small" />
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Box>
                      <Typography variant="body2" fontWeight="medium" sx={{ mb: 0.5 }}>
                        {defect.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {defect.location}
                        {defect.floor && `, ${defect.floor} этаж`}
                        {defect.room && `, ${defect.room}`}
                      </Typography>
                      <Box mt={0.5}>
                        <Chip
                          label={defect.category.name}
                          size="small"
                          sx={{
                            backgroundColor: defect.category.color + '20',
                            color: defect.category.color,
                            border: `1px solid ${defect.category.color}30`
                          }}
                        />
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {defect.project.name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    {getStatusChip(defect.status)}
                  </TableCell>
                  <TableCell>
                    {getPriorityChip(defect.priority)}
                  </TableCell>
                  <TableCell>
                    {defect.assignee ? (
                      <Box display="flex" alignItems="center" gap={1}>
                        <Avatar sx={{ width: 24, height: 24, fontSize: '0.75rem' }}>
                          {defect.assignee.first_name[0]}
                        </Avatar>
                        <Typography variant="body2">
                          {defect.assignee.first_name} {defect.assignee.last_name}
                        </Typography>
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        Не назначен
                      </Typography>
                    )}
                  </TableCell>
                  <TableCell>
                    {getDaysRemainingChip(defect)}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {formatDate(defect.created_at)}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {defect.author.first_name} {defect.author.last_name}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleMenuOpen(e, defect);
                      }}
                    >
                      <MoreVertIcon />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
              
              {defects.length === 0 && !isLoading && (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      Дефекты не найдены
                    </Typography>
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </TableContainer>
        
        <TablePagination
          component="div"
          count={totalCount}
          page={page - 1}
          onPageChange={handlePageChange}
          rowsPerPage={pageSize}
          onRowsPerPageChange={handlePageSizeChange}
          rowsPerPageOptions={[10, 20, 50]}
          labelRowsPerPage="Строк на странице:"
          labelDisplayedRows={({ from, to, count }) => `${from}-${to} из ${count}`}
        />
      </Paper>
      
      {/* Меню действий */}
      <Menu
        anchorEl={menuAnchor}
        open={Boolean(menuAnchor)}
        onClose={handleMenuClose}
      >
        {/* Основные действия */}
        <MenuItem onClick={() => {
          if (selectedDefect) {
            navigate(`/defects/${selectedDefect.id}`);
          }
          handleMenuClose();
        }}>
          <ViewIcon sx={{ mr: 1 }} />
          Просмотр
        </MenuItem>

        <MenuItem onClick={handleAddComment}>
          <CommentIcon sx={{ mr: 1 }} />
          Добавить комментарий
        </MenuItem>

        <MenuItem onClick={handleViewHistory}>
          <HistoryIcon sx={{ mr: 1 }} />
          История изменений
        </MenuItem>

        <Divider />

        {/* Действия редактирования */}
        {permissions.canEdit() && (
          <MenuItem onClick={handleEdit}>
            <EditIcon sx={{ mr: 1 }} />
            Редактировать
          </MenuItem>
        )}
        {permissions.canChangeStatus() && (
          <MenuItem onClick={handleStatusChange}>
            <StatusIcon sx={{ mr: 1 }} />
            Изменить статус
          </MenuItem>
        )}
        {permissions.canAssign() && (
          <MenuItem onClick={handleAssign}>
            <AssignIcon sx={{ mr: 1 }} />
            Назначить исполнителя
          </MenuItem>
        )}

        <Divider />

        {/* Действия с данными */}
        <MenuItem onClick={handleCopyDefect}>
          <CopyIcon sx={{ mr: 1 }} />
          Копировать информацию
        </MenuItem>

        <MenuItem onClick={handleShareDefect}>
          <ShareIcon sx={{ mr: 1 }} />
          Поделиться ссылкой
        </MenuItem>

        <MenuItem onClick={handleExportDefect}>
          <ExportIcon sx={{ mr: 1 }} />
          Экспортировать
        </MenuItem>

        <MenuItem onClick={handlePrintDefect}>
          <PrintIcon sx={{ mr: 1 }} />
          Печать
        </MenuItem>

        <Divider />

        {/* Опасные действия */}
        {permissions.canDelete() && selectedDefect && (
          <MenuItem
            onClick={() => {
              if (window.confirm(`Вы уверены, что хотите удалить дефект "${selectedDefect.title}"?`)) {
                showSnackbar(`Дефект "${selectedDefect.title}" будет удален`, 'error');
                // Здесь была бы логика удаления дефекта через API
                // await dispatch(deleteDefect(selectedDefect.id));
              }
              handleMenuClose();
            }}
            sx={{ color: 'error.main' }}
          >
            <DeleteIcon sx={{ mr: 1 }} />
            Удалить
          </MenuItem>
        )}
      </Menu>
      
      {/* Уведомления */}
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={4000}
        onClose={() => setSnackbarOpen(false)}
      >
        <Alert severity={snackbarSeverity} onClose={() => setSnackbarOpen(false)}>
          {snackbarMessage}
        </Alert>
      </Snackbar>
      
      {/* Диалог создания дефекта */}
      <DefectCreateDialog
        open={createDialogOpen}
        onClose={() => setCreateDialogOpen(false)}
        onSubmit={handleCreateDefect}
        projects={projects}
        users={engineers}
      />
    </Box>
  );
};