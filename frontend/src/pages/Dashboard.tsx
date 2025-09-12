/**
 * Главная страница - дашборд
 */

import React from 'react';
import { 
  Grid, 
  Paper, 
  Typography, 
  Box,
  Card,
  CardContent,
  CardActions,
  Button
} from '@mui/material';
import { 
  BugReport as BugReportIcon,
  Assignment as AssignmentIcon,
  Assessment as AssessmentIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

const StatCard: React.FC<{
  title: string;
  value: number;
  icon: React.ReactNode;
  color: string;
  onClick: () => void;
}> = ({ title, value, icon, color, onClick }) => (
  <Card sx={{ height: '100%', cursor: 'pointer' }} onClick={onClick}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Box sx={{ color, mr: 2 }}>
          {icon}
        </Box>
        <Typography variant="h6" component="div">
          {title}
        </Typography>
      </Box>
      <Typography variant="h3" component="div" color={color}>
        {value}
      </Typography>
    </CardContent>
    <CardActions>
      <Button size="small">Подробнее</Button>
    </CardActions>
  </Card>
);

export const Dashboard: React.FC = () => {
  const navigate = useNavigate();

  return (
    <Box>
      <Typography variant="h4" component="h1" gutterBottom>
        Дашборд
      </Typography>
      
      <Grid container spacing={3}>
        {/* Статистические карточки */}
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Активные дефекты"
            value={42}
            icon={<BugReportIcon fontSize="large" />}
            color="#f44336"
            onClick={() => navigate('/defects')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Проекты"
            value={8}
            icon={<AssignmentIcon fontSize="large" />}
            color="#2196f3"
            onClick={() => navigate('/projects')}
          />
        </Grid>
        
        <Grid item xs={12} sm={6} md={4}>
          <StatCard
            title="Отчеты"
            value={15}
            icon={<AssessmentIcon fontSize="large" />}
            color="#4caf50"
            onClick={() => navigate('/reports')}
          />
        </Grid>

        {/* Последние дефекты */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Последние дефекты
            </Typography>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Здесь будет список последних дефектов...
              </Typography>
            </Box>
          </Paper>
        </Grid>

        {/* Статистика */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Статистика
            </Typography>
            <Box>
              <Typography variant="body2" color="text.secondary">
                Здесь будут графики и диаграммы...
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};