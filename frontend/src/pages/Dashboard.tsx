/**
 * Главная страница - дашборд
 */

import React, { useState, useEffect } from 'react';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider
} from '@mui/material';
import { 
  BugReport as BugReportIcon,
  Assignment as AssignmentIcon,
  Assessment as AssessmentIcon,
  Person as PersonIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Schedule as ScheduleIcon,
  Engineering as EngineeringIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/index';
import { selectDefectsList, fetchDefects } from '../store/slices/defectsSlice';
import { selectProjectsList, fetchProjects } from '../store/slices/projectsSlice';
import { defectsAPI } from '../services/api';

const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  subtitle?: string;
  trend?: string;
  onClick: () => void;
}> = ({ title, value, icon, color, subtitle, trend, onClick }) => (
  <Card sx={{ 
    height: '100%', 
    cursor: 'pointer',
    transition: 'transform 0.2s, box-shadow 0.2s',
    '&:hover': {
      transform: 'translateY(-2px)',
      boxShadow: 4
    }
  }} onClick={onClick}>
    <CardContent>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Box sx={{ color, fontSize: '2.5rem' }}>
          {icon}
        </Box>
        {trend && (
          <Chip 
            label={trend} 
            size="small" 
            color={trend.includes('+') ? 'success' : 'error'}
            variant="outlined"
          />
        )}
      </Box>
      <Typography variant="h3" component="div" color={color} fontWeight="bold">
        {value}
      </Typography>
      <Typography variant="h6" component="div" color="text.primary" mb={1}>
        {title}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
    <CardActions>
      <Button size="small" sx={{ color }}>Подробнее</Button>
    </CardActions>
  </Card>
);

const StatusChart: React.FC<{ defects: any[] }> = ({ defects }) => {
  const statusCounts = {
    new: defects.filter(d => d.status === 'new').length,
    in_progress: defects.filter(d => d.status === 'in_progress').length,
    review: defects.filter(d => d.status === 'review').length,
    closed: defects.filter(d => d.status === 'closed').length,
    cancelled: defects.filter(d => d.status === 'cancelled').length
  };

  const total = Object.values(statusCounts).reduce((a, b) => a + b, 0);

  const statusConfig = [
    { key: 'new', label: 'Новые', color: '#2196f3' },
    { key: 'in_progress', label: 'В работе', color: '#ff9800' },
    { key: 'review', label: 'На проверке', color: '#9c27b0' },
    { key: 'closed', label: 'Закрытые', color: '#4caf50' },
    { key: 'cancelled', label: 'Отмененные', color: '#f44336' }
  ];

  return (
    <Box>
      {statusConfig.map(({ key, label, color }) => {
        const count = statusCounts[key as keyof typeof statusCounts];
        const percentage = total > 0 ? (count / total) * 100 : 0;
        
        return (
          <Box key={key} mb={2}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="body2">{label}</Typography>
              <Typography variant="body2" fontWeight="bold">{count}</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={percentage}
              sx={{
                height: 8,
                borderRadius: 4,
                backgroundColor: 'rgba(0,0,0,0.1)',
                '& .MuiLinearProgress-bar': {
                  backgroundColor: color,
                  borderRadius: 4,
                }
              }}
            />
          </Box>
        );
      })}
    </Box>
  );
};

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  
  const defects = useAppSelector(selectDefectsList) as any[];
  const projects = useAppSelector(selectProjectsList) as any[];
  
  const [loading, setLoading] = useState(true);
  const [recentDefects, setRecentDefects] = useState<any[]>([]);

  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Загружаем данные для дашборда
        await Promise.all([
          dispatch(fetchDefects({ page: 1, pageSize: 10 }) as any),
          dispatch(fetchProjects({}) as any)
        ]);

        // Получаем последние дефекты
        const recent = await defectsAPI.getDefects({ 
          page: 1, 
          pageSize: 5
        } as any);
        setRecentDefects(recent.results || []);
      } catch (error) {
        console.error('Ошибка загрузки данных дашборда:', error);
      } finally {
        setLoading(false);
      }
    };

    loadDashboardData();
  }, [dispatch]);

  const activeDefectsCount = defects.filter(d => 
    ['new', 'in_progress', 'review'].includes(d.status)
  ).length;

  const overdueDefectsCount = defects.filter(d => d.is_overdue).length;

  const myDefectsCount = defects.filter(d => 
    d.assignee?.id === 1 && ['new', 'in_progress'].includes(d.status)
  ).length;

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: string } = {
      'new': '#2196f3',
      'in_progress': '#ff9800',
      'review': '#9c27b0',
      'closed': '#4caf50',
      'cancelled': '#f44336'
    };
    return colors[status] || '#757575';
  };

  const getStatusLabel = (status: string) => {
    const labels: { [key: string]: string } = {
      'new': 'Новый',
      'in_progress': 'В работе',
      'review': 'На проверке',
      'closed': 'Закрыт',
      'cancelled': 'Отменен'
    };
    return labels[status] || status;
  };

  const getPriorityColor = (priority: string) => {
    const colors: { [key: string]: string } = {
      'low': '#4caf50',
      'medium': '#ff9800',
      'high': '#f44336',
      'critical': '#d32f2f'
    };
    return colors[priority] || '#757575';
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress size={60} />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Панель управления
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Обновлено: {new Date().toLocaleString('ru-RU')}
        </Typography>
      </Box>
      
      <Grid container spacing={3}>
        {/* Статистические карточки */}
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Активные дефекты"
            value={activeDefectsCount}
            icon={<BugReportIcon />}
            color="#f44336"
            subtitle="требуют внимания"
            trend={overdueDefectsCount > 0 ? `+${overdueDefectsCount} просрочено` : undefined}
            onClick={() => navigate('/defects?status=new,in_progress,review')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Проекты"
            value={projects.length}
            icon={<AssignmentIcon />}
            color="#2196f3"
            subtitle="в работе"
            onClick={() => navigate('/projects')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Мои задачи"
            value={myDefectsCount}
            icon={<EngineeringIcon />}
            color="#ff9800"
            subtitle="назначено мне"
            onClick={() => navigate('/defects?assignee=me')}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Просрочено"
            value={overdueDefectsCount}
            icon={<WarningIcon />}
            color="#d32f2f"
            subtitle="требуют срочного внимания"
            onClick={() => navigate('/defects?overdue=true')}
          />
        </Grid>

        {/* Последние дефекты */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="h6" fontWeight="bold">
                Последние дефекты
              </Typography>
              <Button 
                size="small" 
                onClick={() => navigate('/defects')}
                sx={{ color: 'primary.main' }}
              >
                Все дефекты
              </Button>
            </Box>
            
            {recentDefects.length > 0 ? (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>№</TableCell>
                      <TableCell>Название</TableCell>
                      <TableCell>Проект</TableCell>
                      <TableCell>Статус</TableCell>
                      <TableCell>Приоритет</TableCell>
                      <TableCell>Создан</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentDefects.slice(0, 5).map((defect) => (
                      <TableRow 
                        key={defect.id}
                        hover
                        sx={{ cursor: 'pointer' }}
                        onClick={() => navigate(`/defects/${defect.id}`)}
                      >
                        <TableCell>{defect.defect_number}</TableCell>
                        <TableCell>
                          <Typography variant="body2" noWrap>
                            {defect.title}
                          </Typography>
                        </TableCell>
                        <TableCell>{defect.project?.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={getStatusLabel(defect.status)}
                            size="small"
                            sx={{
                              backgroundColor: getStatusColor(defect.status),
                              color: 'white',
                              fontWeight: 'bold'
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={defect.priority}
                            size="small"
                            variant="outlined"
                            sx={{
                              borderColor: getPriorityColor(defect.priority),
                              color: getPriorityColor(defect.priority)
                            }}
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2" color="text.secondary">
                            {new Date(defect.created_at).toLocaleDateString('ru-RU')}
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Box textAlign="center" py={4}>
                <Typography variant="body2" color="text.secondary">
                  Нет данных о дефектах
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Статистика по статусам */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" fontWeight="bold" mb={3}>
              Статистика по статусам
            </Typography>
            <StatusChart defects={defects} />
            
            <Divider sx={{ my: 2 }} />
            
            <Box>
              <Typography variant="body2" color="text.secondary" mb={1}>
                Общая статистика
              </Typography>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Всего дефектов:</Typography>
                <Typography variant="body2" fontWeight="bold">{defects.length}</Typography>
              </Box>
              <Box display="flex" justifyContent="space-between" mb={1}>
                <Typography variant="body2">Закрыто за месяц:</Typography>
                <Typography variant="body2" fontWeight="bold" color="success.main">
                  {defects.filter(d => d.status === 'closed').length}
                </Typography>
              </Box>
              <Box display="flex" justifyContent="space-between">
                <Typography variant="body2">Средний срок устранения:</Typography>
                <Typography variant="body2" fontWeight="bold">3.2 дня</Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Быстрые действия */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" fontWeight="bold" mb={2}>
              Быстрые действия
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="contained"
                  startIcon={<BugReportIcon />}
                  fullWidth
                  onClick={() => navigate('/defects?create=true')}
                  sx={{ py: 1.5 }}
                >
                  Создать дефект
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  startIcon={<AssignmentIcon />}
                  fullWidth
                  onClick={() => navigate('/projects?create=true')}
                  sx={{ py: 1.5 }}
                >
                  Новый проект
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  startIcon={<AssessmentIcon />}
                  fullWidth
                  onClick={() => navigate('/reports')}
                  sx={{ py: 1.5 }}
                >
                  Отчеты
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Button
                  variant="outlined"
                  startIcon={<TrendingUpIcon />}
                  fullWidth
                  onClick={() => navigate('/analytics')}
                  sx={{ py: 1.5 }}
                >
                  Аналитика
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};