import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  LinearProgress,
  Chip,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  BugReport,
  Business,
  Assignment,
  TrendingUp,
  CheckCircle,
  Warning,
  Error,
} from '@mui/icons-material';

const HomePage: React.FC = () => {
  // Демо данные
  const stats = {
    totalDefects: 42,
    activeProjects: 8,
    completedTasks: 156,
    pendingReports: 3,
  };

  const recentDefects = [
    {
      id: 1,
      title: 'Трещина в стене на 3 этаже',
      project: 'ЖК Солнечный',
      priority: 'high',
      status: 'new',
    },
    {
      id: 2,
      title: 'Неровность пола в квартире 45',
      project: 'ЖК Березовая роща',
      priority: 'medium',
      status: 'in_progress',
    },
    {
      id: 3,
      title: 'Протечка в санузле',
      project: 'ТЦ Галерея',
      priority: 'critical',
      status: 'review',
    },
  ];

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'new':
        return <Error color="error" />;
      case 'in_progress':
        return <Warning color="warning" />;
      case 'review':
        return <Assignment color="info" />;
      case 'completed':
        return <CheckCircle color="success" />;
      default:
        return <BugReport />;
    }
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Добро пожаловать в систему управления дефектами! 🏗️
      </Typography>
      
      <Typography variant="subtitle1" color="text.secondary" gutterBottom>
        Эффективное управление качеством строительства
      </Typography>

      {/* Статистические карточки */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <BugReport color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Всего дефектов
                  </Typography>
                  <Typography variant="h4">
                    {stats.totalDefects}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Business color="secondary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Активные проекты
                  </Typography>
                  <Typography variant="h4">
                    {stats.activeProjects}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CheckCircle color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Выполнено задач
                  </Typography>
                  <Typography variant="h4">
                    {stats.completedTasks}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <Assignment color="info" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography color="textSecondary" gutterBottom>
                    Ожидают отчёты
                  </Typography>
                  <Typography variant="h4">
                    {stats.pendingReports}
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Последние дефекты */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Последние дефекты
            </Typography>
            
            <List>
              {recentDefects.map((defect) => (
                <ListItem key={defect.id} divider>
                  <ListItemIcon>
                    {getStatusIcon(defect.status)}
                  </ListItemIcon>
                  
                  <ListItemText
                    primary={defect.title}
                    secondary={defect.project}
                  />
                  
                  <Chip
                    label={defect.priority}
                    color={getPriorityColor(defect.priority) as any}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                </ListItem>
              ))}
            </List>
            
            <CardActions>
              <Button size="small" color="primary">
                Посмотреть все дефекты
              </Button>
            </CardActions>
          </Paper>
        </Grid>

        {/* Прогресс проектов */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Прогресс проектов
            </Typography>
            
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">ЖК Солнечный</Typography>
                <Typography variant="body2">75%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={75} />
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">ТЦ Галерея</Typography>
                <Typography variant="body2">60%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={60} />
            </Box>
            
            <Box sx={{ mb: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                <Typography variant="body2">Офисный центр</Typography>
                <Typography variant="body2">90%</Typography>
              </Box>
              <LinearProgress variant="determinate" value={90} />
            </Box>
            
            <CardActions>
              <Button size="small" color="primary">
                Все проекты
              </Button>
            </CardActions>
          </Paper>
        </Grid>
      </Grid>

      {/* Приветственное сообщение */}
      <Paper 
        sx={{ 
          mt: 4, 
          p: 3, 
          background: 'linear-gradient(45deg, #FE6B8B 30%, #FF8E53 90%)',
          color: 'white',
        }}
      >
        <Typography variant="h5" gutterBottom>
          🎉 Система готова к работе!
        </Typography>
        <Typography variant="body1">
          Система управления дефектами полностью настроена и готова к использованию. 
          Вы можете создавать проекты, отслеживать дефекты, генерировать отчёты и управлять командой.
        </Typography>
        <Box sx={{ mt: 2 }}>
          <Button variant="contained" color="secondary" sx={{ mr: 2 }}>
            Создать проект
          </Button>
          <Button variant="outlined" sx={{ color: 'white', borderColor: 'white' }}>
            Посмотреть руководство
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

export default HomePage;

