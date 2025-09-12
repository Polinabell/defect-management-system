/**
 * Страница отчетов и аналитики
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Chip,
  Tab,
  Tabs,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  FileDownload as DownloadIcon,
  Assessment as AssessmentIcon,
  TrendingUp as TrendingUpIcon,
  PieChart as PieChartIcon,
  TableChart as TableChartIcon,
  BarChart as BarChartIcon,
  DateRange as DateRangeIcon,
  FilterList as FilterIcon
} from '@mui/icons-material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
  Area,
  AreaChart
} from 'recharts';
import { CSVLink } from 'react-csv';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { useAppSelector, useAppDispatch } from '../store/index';
import { selectDefectsList, fetchDefects } from '../store/slices/defectsSlice';
import { selectProjectsList, fetchProjects } from '../store/slices/projectsSlice';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`reports-tabpanel-${index}`}
      aria-labelledby={`reports-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export const Reports: React.FC = () => {
  const dispatch = useAppDispatch();
  const defects = useAppSelector(selectDefectsList) as any[];
  const projects = useAppSelector(selectProjectsList) as any[];
  
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 дней назад
    end: new Date().toISOString().split('T')[0] // сегодня
  });
  const [selectedProject, setSelectedProject] = useState<string>('all');

  useEffect(() => {
    const loadReportsData = async () => {
      try {
        await Promise.all([
          dispatch(fetchDefects({ page: 1, pageSize: 1000 }) as any),
          dispatch(fetchProjects({}) as any)
        ]);
      } catch (error) {
        console.error('Ошибка загрузки данных для отчетов:', error);
      } finally {
        setLoading(false);
      }
    };

    loadReportsData();
  }, [dispatch]);

  // Фильтрация данных по дате и проекту
  const filteredDefects = defects.filter(defect => {
    const defectDate = new Date(defect.created_at);
    const startDate = new Date(dateRange.start);
    const endDate = new Date(dateRange.end);
    
    const dateInRange = defectDate >= startDate && defectDate <= endDate;
    const projectMatch = selectedProject === 'all' || defect.project?.id === Number(selectedProject);
    
    return dateInRange && projectMatch;
  });

  // Подготовка данных для графиков
  const statusData = [
    { name: 'Новые', value: filteredDefects.filter(d => d.status === 'new').length, color: '#2196f3' },
    { name: 'В работе', value: filteredDefects.filter(d => d.status === 'in_progress').length, color: '#ff9800' },
    { name: 'На проверке', value: filteredDefects.filter(d => d.status === 'review').length, color: '#9c27b0' },
    { name: 'Закрытые', value: filteredDefects.filter(d => d.status === 'closed').length, color: '#4caf50' },
    { name: 'Отмененные', value: filteredDefects.filter(d => d.status === 'cancelled').length, color: '#f44336' }
  ];

  const priorityData = [
    { name: 'Низкий', value: filteredDefects.filter(d => d.priority === 'low').length },
    { name: 'Средний', value: filteredDefects.filter(d => d.priority === 'medium').length },
    { name: 'Высокий', value: filteredDefects.filter(d => d.priority === 'high').length },
    { name: 'Критический', value: filteredDefects.filter(d => d.priority === 'critical').length }
  ];

  // Данные по месяцам (тренды)
  const monthlyData = React.useMemo(() => {
    const monthsMap: { [key: string]: { created: number; closed: number } } = {};
    
    filteredDefects.forEach(defect => {
      const month = new Date(defect.created_at).toISOString().slice(0, 7); // YYYY-MM
      if (!monthsMap[month]) {
        monthsMap[month] = { created: 0, closed: 0 };
      }
      monthsMap[month].created++;
      
      if (defect.status === 'closed') {
        monthsMap[month].closed++;
      }
    });

    return Object.entries(monthsMap)
      .sort(([a], [b]) => a.localeCompare(b))
      .slice(-6) // последние 6 месяцев
      .map(([month, data]) => ({
        month: new Date(month + '-01').toLocaleDateString('ru-RU', { month: 'short', year: 'numeric' }),
        created: data.created,
        closed: data.closed
      }));
  }, [filteredDefects]);

  const projectsData = projects.map(project => {
    const projectDefects = filteredDefects.filter(d => d.project?.id === project.id);
    return {
      name: project.name,
      defects: projectDefects.length,
      closed: projectDefects.filter(d => d.status === 'closed').length,
      active: projectDefects.filter(d => ['new', 'in_progress', 'review'].includes(d.status)).length
    };
  }).filter(p => p.defects > 0);

  // Подготовка данных для экспорта
  const exportData = filteredDefects.map(defect => ({
    'Номер дефекта': defect.defect_number,
    'Название': defect.title,
    'Проект': defect.project?.name || '',
    'Статус': defect.status,
    'Приоритет': defect.priority,
    'Серьезность': defect.severity,
    'Категория': defect.category,
    'Исполнитель': defect.assignee ? `${defect.assignee.first_name} ${defect.assignee.last_name}` : '',
    'Автор': defect.reporter ? `${defect.reporter.first_name} ${defect.reporter.last_name}` : '',
    'Дата создания': new Date(defect.created_at).toLocaleDateString('ru-RU'),
    'Дата обновления': new Date(defect.updated_at).toLocaleDateString('ru-RU'),
    'Срок выполнения': defect.due_date ? new Date(defect.due_date).toLocaleDateString('ru-RU') : '',
    'Просрочен': defect.is_overdue ? 'Да' : 'Нет'
  }));

  const csvHeaders = [
    { label: 'Номер дефекта', key: 'Номер дефекта' },
    { label: 'Название', key: 'Название' },
    { label: 'Проект', key: 'Проект' },
    { label: 'Статус', key: 'Статус' },
    { label: 'Приоритет', key: 'Приоритет' },
    { label: 'Серьезность', key: 'Серьезность' },
    { label: 'Категория', key: 'Категория' },
    { label: 'Исполнитель', key: 'Исполнитель' },
    { label: 'Автор', key: 'Автор' },
    { label: 'Дата создания', key: 'Дата создания' },
    { label: 'Дата обновления', key: 'Дата обновления' },
    { label: 'Срок выполнения', key: 'Срок выполнения' },
    { label: 'Просрочен', key: 'Просрочен' }
  ];

  const exportToExcel = () => {
    const ws = XLSX.utils.json_to_sheet(exportData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Отчет по дефектам');
    
    // Настройка ширины колонок
    const maxWidths = exportData.reduce((widths: any, row: any) => {
      Object.keys(row).forEach((key, index) => {
        const cellValue = String(row[key] || '');
        widths[index] = Math.max(widths[index] || 10, cellValue.length + 2);
      });
      return widths;
    }, {});
    
    ws['!cols'] = Object.values(maxWidths).map((width: any) => ({ width: Math.min(width, 50) }));
    
    const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    const dataBlob = new Blob([excelBuffer], { type: 'application/octet-stream' });
    const fileName = `defects_report_${new Date().toISOString().split('T')[0]}.xlsx`;
    saveAs(dataBlob, fileName);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
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
      {/* Заголовок и фильтры */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1" fontWeight="bold">
          Отчеты и аналитика
        </Typography>
        
        <Box display="flex" gap={2} alignItems="center">
          <CSVLink
            data={exportData}
            headers={csvHeaders}
            filename={`defects_report_${new Date().toISOString().split('T')[0]}.csv`}
            style={{ textDecoration: 'none' }}
          >
            <Button
              variant="outlined"
              startIcon={<DownloadIcon />}
              size="small"
            >
              CSV
            </Button>
          </CSVLink>
          
          <Button
            variant="outlined"
            startIcon={<DownloadIcon />}
            onClick={exportToExcel}
            size="small"
          >
            Excel
          </Button>
        </Box>
      </Box>

      {/* Фильтры */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Фильтры отчета
        </Typography>
        
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} sm={4}>
            <TextField
              label="Дата начала"
              type="date"
              value={dateRange.start}
              onChange={(e) => setDateRange(prev => ({ ...prev, start: e.target.value }))}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <TextField
              label="Дата окончания"
              type="date"
              value={dateRange.end}
              onChange={(e) => setDateRange(prev => ({ ...prev, end: e.target.value }))}
              fullWidth
              InputLabelProps={{ shrink: true }}
            />
          </Grid>
          
          <Grid item xs={12} sm={4}>
            <FormControl fullWidth>
              <InputLabel>Проект</InputLabel>
              <Select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                label="Проект"
              >
                <MenuItem value="all">Все проекты</MenuItem>
                {projects.map(project => (
                  <MenuItem key={project.id} value={project.id.toString()}>
                    {project.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
        </Grid>

        <Box mt={2} display="flex" gap={2} alignItems="center">
          <Typography variant="body2" color="text.secondary">
            Найдено дефектов: {filteredDefects.length}
          </Typography>
          <Chip 
            label={`${filteredDefects.filter(d => d.status === 'closed').length} закрыто`}
            color="success"
            size="small"
          />
          <Chip 
            label={`${filteredDefects.filter(d => d.is_overdue).length} просрочено`}
            color="error"
            size="small"
          />
        </Box>
      </Paper>

      {/* Вкладки */}
      <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab icon={<BarChartIcon />} label="Общая статистика" />
          <Tab icon={<TrendingUpIcon />} label="Тренды" />
          <Tab icon={<PieChartIcon />} label="Распределение" />
          <Tab icon={<TableChartIcon />} label="Детальные данные" />
        </Tabs>
      </Box>

      {/* Общая статистика */}
      <TabPanel value={tabValue} index={0}>
        <Grid container spacing={3}>
          {/* Основные метрики */}
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold" color="primary.main">
                      {filteredDefects.length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Всего дефектов
                    </Typography>
                  </Box>
                  <AssessmentIcon color="primary" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold" color="success.main">
                      {filteredDefects.filter(d => d.status === 'closed').length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Закрыто
                    </Typography>
                  </Box>
                  <AssessmentIcon color="success" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold" color="warning.main">
                      {filteredDefects.filter(d => ['new', 'in_progress', 'review'].includes(d.status)).length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      В работе
                    </Typography>
                  </Box>
                  <AssessmentIcon color="warning" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" justifyContent="space-between">
                  <Box>
                    <Typography variant="h4" fontWeight="bold" color="error.main">
                      {filteredDefects.filter(d => d.is_overdue).length}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Просрочено
                    </Typography>
                  </Box>
                  <AssessmentIcon color="error" sx={{ fontSize: 40 }} />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          {/* Статистика по статусам */}
          <Grid item xs={12} md={8}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Дефекты по статусам
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={statusData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="value" fill="#8884d8">
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          {/* Статистика по приоритетам */}
          <Grid item xs={12} md={4}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                По приоритетам
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={priorityData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    label
                  >
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Тренды */}
      <TabPanel value={tabValue} index={1}>
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Динамика создания и закрытия дефектов
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <AreaChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <RechartsTooltip />
                  <Area
                    type="monotone"
                    dataKey="created"
                    stackId="1"
                    stroke="#ff7300"
                    fill="#ff7300"
                    name="Создано"
                  />
                  <Area
                    type="monotone"
                    dataKey="closed"
                    stackId="1"
                    stroke="#387908"
                    fill="#387908"
                    name="Закрыто"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Статистика по проектам
              </Typography>
              <ResponsiveContainer width="100%" height={400}>
                <BarChart data={projectsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar dataKey="defects" name="Всего дефектов" fill="#8884d8" />
                  <Bar dataKey="closed" name="Закрыто" fill="#82ca9d" />
                  <Bar dataKey="active" name="Активные" fill="#ffc658" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Распределение */}
      <TabPanel value={tabValue} index={2}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Распределение по статусам
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={statusData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {statusData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>

          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Распределение по приоритетам
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={priorityData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    fill="#8884d8"
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {priorityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        </Grid>
      </TabPanel>

      {/* Детальные данные */}
      <TabPanel value={tabValue} index={3}>
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Детальная таблица дефектов
          </Typography>
          
          <TableContainer sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell>№</TableCell>
                  <TableCell>Название</TableCell>
                  <TableCell>Проект</TableCell>
                  <TableCell>Статус</TableCell>
                  <TableCell>Приоритет</TableCell>
                  <TableCell>Исполнитель</TableCell>
                  <TableCell>Создан</TableCell>
                  <TableCell>Срок</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {filteredDefects.slice(0, 100).map((defect) => (
                  <TableRow key={defect.id} hover>
                    <TableCell>{defect.defect_number}</TableCell>
                    <TableCell>
                      <Typography variant="body2" noWrap title={defect.title}>
                        {defect.title.length > 50 ? defect.title.substring(0, 50) + '...' : defect.title}
                      </Typography>
                    </TableCell>
                    <TableCell>{defect.project?.name}</TableCell>
                    <TableCell>
                      <Chip
                        label={defect.status}
                        size="small"
                        color={
                          defect.status === 'closed' ? 'success' :
                          defect.status === 'in_progress' ? 'primary' :
                          defect.status === 'review' ? 'warning' :
                          defect.status === 'cancelled' ? 'error' : 'default'
                        }
                      />
                    </TableCell>
                    <TableCell>
                      <Chip
                        label={defect.priority}
                        size="small"
                        variant="outlined"
                        color={
                          defect.priority === 'critical' ? 'error' :
                          defect.priority === 'high' ? 'warning' :
                          defect.priority === 'medium' ? 'primary' : 'default'
                        }
                      />
                    </TableCell>
                    <TableCell>
                      {defect.assignee ? `${defect.assignee.first_name} ${defect.assignee.last_name}` : '-'}
                    </TableCell>
                    <TableCell>
                      {new Date(defect.created_at).toLocaleDateString('ru-RU')}
                    </TableCell>
                    <TableCell>
                      {defect.due_date ? (
                        <Typography 
                          variant="body2" 
                          color={defect.is_overdue ? 'error.main' : 'text.primary'}
                        >
                          {new Date(defect.due_date).toLocaleDateString('ru-RU')}
                        </Typography>
                      ) : '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          {filteredDefects.length > 100 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              Показаны первые 100 записей из {filteredDefects.length}. 
              Используйте фильтры для уточнения результатов или экспортируйте все данные.
            </Alert>
          )}
        </Paper>
      </TabPanel>
    </Box>
  );
};