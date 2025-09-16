/**
 * Страница управления проектами
 */

import React, { useEffect, useState } from 'react';
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
  Chip,
  IconButton,
  TextField,
  Grid,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Pagination,
  Tooltip,
  LinearProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as ViewIcon,
  Search as SearchIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import { useDispatch, useSelector } from 'react-redux';
import { useSearchParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import {
  fetchProjects,
  createProject,
  updateProject,
  deleteProject,
  setFilters,
  clearFilters,
  setPage,
  selectProjectsList,
  selectProjectsLoading,
  selectProjectsError,
  selectProjectsFilters,
  selectProjectsPagination,
  Project
} from '../store/slices/projectsSlice';

export const Projects: React.FC = () => {
  const dispatch = useDispatch();
  const { hasPermission } = useAuth();
  const { showSuccess, showError } = useNotification();
  const [searchParams, setSearchParams] = useSearchParams();
  
  const projects = useSelector(selectProjectsList);
  const isLoading = useSelector(selectProjectsLoading);
  const filters = useSelector(selectProjectsFilters);
  const pagination = useSelector(selectProjectsPagination) as {
    page: number;
    pageSize: number;
    totalCount: number;
  };
  
  const [openDialog, setOpenDialog] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  
  const [projectForm, setProjectForm] = useState({
    name: '',
    description: '',
    status: 'planning' as Project['status'],
    priority: 'medium' as Project['priority'],
    start_date: '',
    end_date: '',
    members_count: 0
  });

  // Загрузка проектов при монтировании
  useEffect(() => {
    dispatch(fetchProjects({}) as any);
  }, [dispatch]);

  // Обновление результатов при изменении фильтров
  useEffect(() => {
    dispatch(fetchProjects({
      ...filters,
      search: searchTerm,
      page: pagination.page
    }) as any);
  }, [dispatch, filters, searchTerm, pagination.page]);

  // Проверка URL параметра для автоматического открытия диалога создания
  useEffect(() => {
    const shouldCreate = searchParams.get('create');
    if (shouldCreate === 'true' && hasPermission('create_project')) {
      setOpenDialog(true);
      // Убираем параметр из URL после открытия диалога
      const newSearchParams = new URLSearchParams(searchParams);
      newSearchParams.delete('create');
      setSearchParams(newSearchParams);
    }
  }, [searchParams, setSearchParams, hasPermission]);

  const handleOpenDialog = (project?: Project) => {
    if (project) {
      setEditingProject(project);
      setProjectForm({
        name: project.name,
        description: project.description,
        status: project.status,
        priority: project.priority,
        start_date: project.start_date,
        end_date: project.end_date || '',
        members_count: project.members_count
      });
    } else {
      setEditingProject(null);
      setProjectForm({
        name: '',
        description: '',
        status: 'planning',
        priority: 'medium',
        start_date: '',
        end_date: '',
        members_count: 0
      });
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setEditingProject(null);
  };

  const handleSubmitProject = async () => {
    try {
      if (editingProject) {
        await dispatch(updateProject({ 
          id: editingProject.id, 
          data: projectForm 
        }) as any);
        showSuccess('Проект успешно обновлен');
      } else {
        await dispatch(createProject(projectForm) as any);
        showSuccess('Проект успешно создан');
      }
      handleCloseDialog();
    } catch (err) {
      showError('Ошибка при сохранении проекта');
    }
  };

  const handleDeleteProject = async (id: number) => {
    if (window.confirm('Вы уверены, что хотите удалить этот проект?')) {
      try {
        await dispatch(deleteProject(id) as any);
        showSuccess('Проект успешно удален');
      } catch (err) {
        showError('Ошибка при удалении проекта');
      }
    }
  };

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'planning': return 'info';
      case 'in_progress': return 'primary';
      case 'on_hold': return 'warning';
      case 'completed': return 'success';
      case 'cancelled': return 'error';
      default: return 'default';
    }
  };

  const getStatusText = (status: Project['status']) => {
    switch (status) {
      case 'planning': return 'Планирование';
      case 'in_progress': return 'В работе';
      case 'on_hold': return 'Приостановлен';
      case 'completed': return 'Завершен';
      case 'cancelled': return 'Отменен';
      default: return status;
    }
  };

  const getPriorityColor = (priority: Project['priority']) => {
    switch (priority) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      case 'critical': return 'error';
      default: return 'default';
    }
  };

  const getPriorityText = (priority: Project['priority']) => {
    switch (priority) {
      case 'low': return 'Низкий';
      case 'medium': return 'Средний';
      case 'high': return 'Высокий';
      case 'critical': return 'Критический';
      default: return priority;
    }
  };

  return (
    <Box>
      {/* Заголовок и кнопка создания */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Проекты
        </Typography>
        {hasPermission('create_project') && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => handleOpenDialog()}
          >
            Добавить проект
          </Button>
        )}
      </Box>

      {/* Карточки статистики */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Всего проектов
              </Typography>
              <Typography variant="h4">
                {pagination.totalCount}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                В работе
              </Typography>
              <Typography variant="h4">
                {projects.filter(p => p.status === 'in_progress').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Завершенные
              </Typography>
              <Typography variant="h4">
                {projects.filter(p => p.status === 'completed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Средний прогресс
              </Typography>
              <Typography variant="h4">
                {projects.length > 0 ? Math.round(projects.reduce((sum, p) => sum + p.progress_percentage, 0) / projects.length) : 0}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Поиск и фильтры */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              placeholder="Поиск проектов..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary' }} />
              }}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Box display="flex" gap={1}>
              <Button
                variant="outlined"
                startIcon={<FilterIcon />}
                onClick={() => setShowFilters(!showFilters)}
              >
                Фильтры
              </Button>
              <Button
                variant="text"
                onClick={() => {
                  dispatch(clearFilters());
                  setSearchTerm('');
                }}
              >
                Сбросить
              </Button>
            </Box>
          </Grid>
        </Grid>

        {/* Развернутые фильтры */}
        {showFilters && (
          <Grid container spacing={2} sx={{ mt: 2 }}>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Статус</InputLabel>
                <Select
                  multiple
                  value={filters.status || []}
                  onChange={(e) => dispatch(setFilters({ status: e.target.value as string[] }))}
                  renderValue={(selected) => selected.map(s => getStatusText(s as Project['status'])).join(', ')}
                >
                  <MenuItem value="planning">Планирование</MenuItem>
                  <MenuItem value="in_progress">В работе</MenuItem>
                  <MenuItem value="on_hold">Приостановлен</MenuItem>
                  <MenuItem value="completed">Завершен</MenuItem>
                  <MenuItem value="cancelled">Отменен</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Приоритет</InputLabel>
                <Select
                  multiple
                  value={filters.priority || []}
                  onChange={(e) => dispatch(setFilters({ priority: e.target.value as string[] }))}
                  renderValue={(selected) => selected.map(p => getPriorityText(p as Project['priority'])).join(', ')}
                >
                  <MenuItem value="low">Низкий</MenuItem>
                  <MenuItem value="medium">Средний</MenuItem>
                  <MenuItem value="high">Высокий</MenuItem>
                  <MenuItem value="critical">Критический</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        )}
      </Paper>

      {/* Таблица проектов */}
      <Paper>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Название</TableCell>
                <TableCell>Статус</TableCell>
                <TableCell>Приоритет</TableCell>
                <TableCell>Менеджер</TableCell>
                <TableCell>Прогресс</TableCell>
                <TableCell>Дефекты</TableCell>
                <TableCell>Участники</TableCell>
                <TableCell>Дата окончания</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {isLoading ? (
                <TableRow>
                  <TableCell colSpan={9}>
                    <LinearProgress />
                  </TableCell>
                </TableRow>
              ) : projects.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center">
                    <Typography variant="body2" color="text.secondary">
                      Проекты не найдены
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                projects.map((project) => (
                  <TableRow key={project.id}>
                    <TableCell>
                      <Box>
                        <Typography variant="subtitle2">{project.name}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {project.description.slice(0, 60)}...
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getStatusText(project.status)}
                        color={getStatusColor(project.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={getPriorityText(project.priority)}
                        color={getPriorityColor(project.priority) as any}
                        size="small"
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {project.manager.first_name} {project.manager.last_name}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <LinearProgress
                          variant="determinate"
                          value={project.progress_percentage}
                          sx={{ width: 60, height: 6 }}
                        />
                        <Typography variant="body2">
                          {project.progress_percentage}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>{project.defects_count}</TableCell>
                    <TableCell>{project.members_count}</TableCell>
                    <TableCell>
                      {project.end_date ? new Date(project.end_date).toLocaleDateString('ru-RU') : '—'}
                    </TableCell>
                    <TableCell>
                      <Box display="flex" gap={0.5}>
                        <Tooltip title="Просмотр">
                          <IconButton size="small">
                            <ViewIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {hasPermission('update_project') && (
                          <Tooltip title="Редактировать">
                            <IconButton
                              size="small"
                              onClick={() => handleOpenDialog(project)}
                            >
                              <EditIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                        {hasPermission('delete_project') && (
                          <Tooltip title="Удалить">
                            <IconButton
                              size="small"
                              onClick={() => handleDeleteProject(project.id)}
                              color="error"
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Пагинация */}
        {pagination.totalCount > pagination.pageSize && (
          <Box display="flex" justifyContent="center" p={2}>
            <Pagination
              count={Math.ceil(pagination.totalCount / pagination.pageSize)}
              page={pagination.page}
              onChange={(_, page) => dispatch(setPage(page))}
            />
          </Box>
        )}
      </Paper>

      {/* Диалог создания/редактирования проекта */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingProject ? 'Редактировать проект' : 'Создать проект'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Название проекта"
                value={projectForm.name}
                onChange={(e) => setProjectForm({...projectForm, name: e.target.value})}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Описание"
                multiline
                rows={3}
                value={projectForm.description}
                onChange={(e) => setProjectForm({...projectForm, description: e.target.value})}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Статус</InputLabel>
                <Select
                  value={projectForm.status}
                  onChange={(e) => setProjectForm({...projectForm, status: e.target.value as Project['status']})}
                >
                  <MenuItem value="planning">Планирование</MenuItem>
                  <MenuItem value="in_progress">В работе</MenuItem>
                  <MenuItem value="on_hold">Приостановлен</MenuItem>
                  <MenuItem value="completed">Завершен</MenuItem>
                  <MenuItem value="cancelled">Отменен</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Приоритет</InputLabel>
                <Select
                  value={projectForm.priority}
                  onChange={(e) => setProjectForm({...projectForm, priority: e.target.value as Project['priority']})}
                >
                  <MenuItem value="low">Низкий</MenuItem>
                  <MenuItem value="medium">Средний</MenuItem>
                  <MenuItem value="high">Высокий</MenuItem>
                  <MenuItem value="critical">Критический</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Дата начала"
                type="date"
                value={projectForm.start_date}
                onChange={(e) => setProjectForm({...projectForm, start_date: e.target.value})}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Дата окончания"
                type="date"
                value={projectForm.end_date}
                onChange={(e) => setProjectForm({...projectForm, end_date: e.target.value})}
                InputLabelProps={{ shrink: true }}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Количество участников"
                type="number"
                value={projectForm.members_count}
                onChange={(e) => setProjectForm({...projectForm, members_count: parseInt(e.target.value) || 0})}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Отмена</Button>
          <Button
            variant="contained"
            onClick={handleSubmitProject}
            disabled={!projectForm.name}
          >
            {editingProject ? 'Сохранить' : 'Создать'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};