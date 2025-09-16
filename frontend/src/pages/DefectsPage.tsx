import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  Avatar,
} from '@mui/material';
import {
  Add,
  Edit,
  Delete,
  Visibility,
  BugReport,
  Warning,
  CheckCircle,
  Error,
} from '@mui/icons-material';

interface Defect {
  id: number;
  title: string;
  description: string;
  project: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  status: 'new' | 'in_progress' | 'review' | 'completed' | 'cancelled';
  assignee: string;
  created_at: string;
  due_date: string;
}

const DefectsPage: React.FC = () => {
  const [defects, setDefects] = useState<Defect[]>([
    {
      id: 1,
      title: 'Трещина в стене на 3 этаже',
      description: 'Обнаружена трещина в несущей стене',
      project: 'ЖК Солнечный',
      priority: 'high',
      status: 'new',
      assignee: 'Иванов И.И.',
      created_at: '2024-01-15',
      due_date: '2024-01-25',
    },
    {
      id: 2,
      title: 'Неровность пола в квартире 45',
      description: 'Пол имеет значительный уклон',
      project: 'ЖК Березовая роща',
      priority: 'medium',
      status: 'in_progress',
      assignee: 'Петров П.П.',
      created_at: '2024-01-14',
      due_date: '2024-01-20',
    },
    {
      id: 3,
      title: 'Протечка в санузле',
      description: 'Обнаружена протечка в трубопроводе',
      project: 'ТЦ Галерея',
      priority: 'critical',
      status: 'review',
      assignee: 'Сидоров С.С.',
      created_at: '2024-01-13',
      due_date: '2024-01-18',
    },
  ]);

  const [openDialog, setOpenDialog] = useState(false);
  const [selectedDefect, setSelectedDefect] = useState<Defect | null>(null);
  const [isCreating, setIsCreating] = useState(false);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new':
        return 'error';
      case 'in_progress':
        return 'warning';
      case 'review':
        return 'info';
      case 'completed':
        return 'success';
      case 'cancelled':
        return 'default';
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
        return <Visibility color="info" />;
      case 'completed':
        return <CheckCircle color="success" />;
      default:
        return <BugReport />;
    }
  };

  const handleCreateDefect = () => {
    setSelectedDefect(null);
    setIsCreating(true);
    setOpenDialog(true);
  };

  const handleEditDefect = (defect: Defect) => {
    setSelectedDefect(defect);
    setIsCreating(false);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedDefect(null);
    setIsCreating(false);
  };

  const handleSaveDefect = () => {
    // Здесь будет логика сохранения дефекта
    console.log('Сохранение дефекта');
    handleCloseDialog();
  };

  const handleDeleteDefect = (id: number) => {
    setDefects(defects.filter(defect => defect.id !== id));
  };

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Управление дефектами 🐛
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleCreateDefect}
        >
          Создать дефект
        </Button>
      </Box>

      {/* Статистика */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ bgcolor: 'error.main', mx: 'auto', mb: 1 }}>
                <Error />
              </Avatar>
              <Typography variant="h6">Новые</Typography>
              <Typography variant="h4">
                {defects.filter(d => d.status === 'new').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ bgcolor: 'warning.main', mx: 'auto', mb: 1 }}>
                <Warning />
              </Avatar>
              <Typography variant="h6">В работе</Typography>
              <Typography variant="h4">
                {defects.filter(d => d.status === 'in_progress').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ bgcolor: 'info.main', mx: 'auto', mb: 1 }}>
                <Visibility />
              </Avatar>
              <Typography variant="h6">На проверке</Typography>
              <Typography variant="h4">
                {defects.filter(d => d.status === 'review').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <Card>
            <CardContent sx={{ textAlign: 'center' }}>
              <Avatar sx={{ bgcolor: 'success.main', mx: 'auto', mb: 1 }}>
                <CheckCircle />
              </Avatar>
              <Typography variant="h6">Завершено</Typography>
              <Typography variant="h4">
                {defects.filter(d => d.status === 'completed').length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Таблица дефектов */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Название</TableCell>
              <TableCell>Проект</TableCell>
              <TableCell>Приоритет</TableCell>
              <TableCell>Статус</TableCell>
              <TableCell>Исполнитель</TableCell>
              <TableCell>Срок</TableCell>
              <TableCell>Действия</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {defects.map((defect) => (
              <TableRow key={defect.id} hover>
                <TableCell>{defect.id}</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    {getStatusIcon(defect.status)}
                    <Box sx={{ ml: 1 }}>
                      <Typography variant="body2" fontWeight="bold">
                        {defect.title}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {defect.description}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell>{defect.project}</TableCell>
                <TableCell>
                  <Chip
                    label={defect.priority}
                    color={getPriorityColor(defect.priority) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={defect.status}
                    color={getStatusColor(defect.status) as any}
                    size="small"
                  />
                </TableCell>
                <TableCell>{defect.assignee}</TableCell>
                <TableCell>{defect.due_date}</TableCell>
                <TableCell>
                  <IconButton
                    size="small"
                    onClick={() => handleEditDefect(defect)}
                  >
                    <Edit />
                  </IconButton>
                  <IconButton
                    size="small"
                    color="error"
                    onClick={() => handleDeleteDefect(defect.id)}
                  >
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Диалог создания/редактирования дефекта */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {isCreating ? 'Создать новый дефект' : 'Редактировать дефект'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Название дефекта"
                defaultValue={selectedDefect?.title || ''}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Описание"
                defaultValue={selectedDefect?.description || ''}
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Проект</InputLabel>
                <Select
                  defaultValue={selectedDefect?.project || ''}
                  label="Проект"
                >
                  <MenuItem value="ЖК Солнечный">ЖК Солнечный</MenuItem>
                  <MenuItem value="ЖК Березовая роща">ЖК Березовая роща</MenuItem>
                  <MenuItem value="ТЦ Галерея">ТЦ Галерея</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Приоритет</InputLabel>
                <Select
                  defaultValue={selectedDefect?.priority || 'medium'}
                  label="Приоритет"
                >
                  <MenuItem value="low">Низкий</MenuItem>
                  <MenuItem value="medium">Средний</MenuItem>
                  <MenuItem value="high">Высокий</MenuItem>
                  <MenuItem value="critical">Критический</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Статус</InputLabel>
                <Select
                  defaultValue={selectedDefect?.status || 'new'}
                  label="Статус"
                >
                  <MenuItem value="new">Новый</MenuItem>
                  <MenuItem value="in_progress">В работе</MenuItem>
                  <MenuItem value="review">На проверке</MenuItem>
                  <MenuItem value="completed">Завершён</MenuItem>
                  <MenuItem value="cancelled">Отменён</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Исполнитель"
                defaultValue={selectedDefect?.assignee || ''}
              />
            </Grid>
            
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="date"
                label="Срок выполнения"
                InputLabelProps={{ shrink: true }}
                defaultValue={selectedDefect?.due_date || ''}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Отмена</Button>
          <Button onClick={handleSaveDefect} variant="contained">
            {isCreating ? 'Создать' : 'Сохранить'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DefectsPage;

