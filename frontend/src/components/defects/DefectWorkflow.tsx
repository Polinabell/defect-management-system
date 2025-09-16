/**
 * Компонент управления workflow дефектов
 */

import React, { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Paper,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Avatar,
  Alert,
  LinearProgress
} from '@mui/material';
import {
  PlayArrow,
  Visibility,
  Check,
  Close,
  History,
  Assignment,
  Comment as CommentIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import {
  Timeline,
  TimelineItem,
  TimelineOppositeContent,
  TimelineSeparator,
  TimelineDot,
  TimelineConnector,
  TimelineContent,
} from '@mui/lab';
import { Defect } from '../../types';

interface DefectWorkflowProps {
  defect: Defect;
  onStatusChange: (defectId: number, newStatus: string, comment?: string) => Promise<void>;
  canManageDefects?: boolean;
  statusHistory?: any[];
}

const DEFECT_STATUSES = [
  { 
    key: 'new', 
    label: 'Новый', 
    icon: <Assignment />, 
    color: 'info' as const,
    description: 'Дефект зарегистрирован и ожидает назначения исполнителя'
  },
  { 
    key: 'in_progress', 
    label: 'В работе', 
    icon: <PlayArrow />, 
    color: 'primary' as const,
    description: 'Дефект находится в работе у исполнителя'
  },
  { 
    key: 'review', 
    label: 'На проверке', 
    icon: <Visibility />, 
    color: 'warning' as const,
    description: 'Дефект на проверке у ответственного'
  },
  { 
    key: 'closed', 
    label: 'Закрыт', 
    icon: <Check />, 
    color: 'success' as const,
    description: 'Дефект успешно исправлен и закрыт'
  },
  { 
    key: 'cancelled', 
    label: 'Отменён', 
    icon: <Close />, 
    color: 'error' as const,
    description: 'Дефект отменён или признан недействительным'
  },
];

const getStatusIndex = (status: string) => {
  const index = DEFECT_STATUSES.findIndex(s => s.key === status);
  return index === -1 ? 0 : index;
};

const getAvailableTransitions = (currentStatus: string, userRole?: string) => {
  const baseTransitions: { [key: string]: string[] } = {
    'new': ['in_progress', 'cancelled'],
    'in_progress': ['review', 'cancelled'],
    'review': ['closed', 'in_progress', 'cancelled'],
    'closed': ['in_progress'], // переоткрытие
    'cancelled': ['new'] // восстановление
  };

  let transitions = baseTransitions[currentStatus] || [];

  // Ограничения по ролям
  if (userRole === 'observer') {
    transitions = []; // наблюдатели не могут изменять статусы
  } else if (userRole === 'engineer') {
    // Инженеры могут только брать в работу и отправлять на проверку
    if (currentStatus === 'new') {
      transitions = ['in_progress'];
    } else if (currentStatus === 'in_progress') {
      transitions = ['review'];
    } else {
      transitions = [];
    }
  }

  return transitions;
};

const getStatusProgress = (status: string): number => {
  const progressMap: { [key: string]: number } = {
    'new': 20,
    'in_progress': 50,
    'review': 80,
    'closed': 100,
    'cancelled': 0
  };
  return progressMap[status] || 0;
};

export const DefectWorkflow: React.FC<DefectWorkflowProps> = ({
  defect,
  onStatusChange,
  canManageDefects = false,
  statusHistory = []
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState('');
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);

  const activeStep = getStatusIndex(defect.status);
  const availableTransitions = getAvailableTransitions(defect.status);
  const currentStatusConfig = DEFECT_STATUSES.find(s => s.key === defect.status);
  const progress = getStatusProgress(defect.status);

  const handleStatusChangeRequest = (newStatus: string) => {
    setSelectedStatus(newStatus);
    setComment('');
    setDialogOpen(true);
  };

  const handleConfirmStatusChange = async () => {
    if (!selectedStatus) return;

    setLoading(true);
    try {
      await onStatusChange(defect.id, selectedStatus, comment);
      setDialogOpen(false);
      setComment('');
    } catch (error) {
      console.error('Ошибка изменения статуса:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusActionLabel = (statusKey: string) => {
    switch (statusKey) {
      case 'in_progress':
        return defect.status === 'closed' ? 'Переоткрыть' : 
               defect.status === 'review' ? 'Вернуть в работу' : 'Взять в работу';
      case 'new':
        return 'Восстановить';
      case 'review':
        return 'Отправить на проверку';
      case 'closed':
        return 'Закрыть дефект';
      case 'cancelled':
        return 'Отменить дефект';
      default:
        const config = DEFECT_STATUSES.find(s => s.key === statusKey);
        return `Перевести в "${config?.label}"`;
    }
  };

  const isOverdue = defect.due_date && new Date(defect.due_date) < new Date();

  return (
    <Box>
      {/* Заголовок и текущий статус */}
      <Paper elevation={2} sx={{ p: 3, mb: 2 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6" fontWeight="bold">
              Workflow дефекта #{defect.defect_number}
            </Typography>
            <Chip
              icon={currentStatusConfig?.icon}
              label={currentStatusConfig?.label || defect.status}
              color={currentStatusConfig?.color || 'default'}
              variant="filled"
              size="medium"
            />
          </Box>
          
          {isOverdue && (
            <Chip
              icon={<WarningIcon />}
              label="Просрочен"
              color="error"
              variant="outlined"
            />
          )}
        </Box>

        {/* Прогресс-бар */}
        <Box mb={3}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
            <Typography variant="body2" color="text.secondary">
              Прогресс выполнения
            </Typography>
            <Typography variant="body2" fontWeight="bold">
              {progress}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(0,0,0,0.1)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4,
                backgroundColor: currentStatusConfig?.color === 'error' ? '#f44336' :
                                currentStatusConfig?.color === 'success' ? '#4caf50' :
                                currentStatusConfig?.color === 'warning' ? '#ff9800' :
                                '#2196f3'
              }
            }}
          />
        </Box>

        {/* Информация о дефекте */}
        <Box display="flex" gap={4} mb={3}>
          <Box>
            <Typography variant="caption" color="text.secondary">
              Создан
            </Typography>
            <Typography variant="body2">
              {new Date(defect.created_at).toLocaleDateString('ru-RU')}
            </Typography>
          </Box>
          
          {defect.due_date && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                Срок выполнения
              </Typography>
              <Typography 
                variant="body2" 
                color={isOverdue ? 'error.main' : 'text.primary'}
                fontWeight={isOverdue ? 'bold' : 'normal'}
              >
                {new Date(defect.due_date).toLocaleDateString('ru-RU')}
              </Typography>
            </Box>
          )}
          
          {defect.assignee && (
            <Box>
              <Typography variant="caption" color="text.secondary">
                Исполнитель
              </Typography>
              <Box display="flex" alignItems="center" gap={1}>
                <Avatar sx={{ width: 20, height: 20 }}>
                  <PersonIcon sx={{ fontSize: 14 }} />
                </Avatar>
                <Typography variant="body2">
                  {defect.assignee.first_name} {defect.assignee.last_name}
                </Typography>
              </Box>
            </Box>
          )}
        </Box>

        {/* Пошаговый workflow */}
        <Stepper activeStep={activeStep} orientation="horizontal" sx={{ mb: 2 }}>
          {DEFECT_STATUSES.filter(s => !['cancelled'].includes(s.key)).map((status, index) => (
            <Step key={status.key} completed={index < activeStep}>
              <StepLabel
                icon={status.icon}
                StepIconProps={{
                  style: {
                    color: index <= activeStep ? 
                      (status.color === 'info' ? '#2196f3' :
                       status.color === 'primary' ? '#1976d2' :
                       status.color === 'warning' ? '#ed6c02' :
                       status.color === 'success' ? '#2e7d32' : '#757575') : '#757575'
                  }
                }}
              >
                <Typography variant="caption" fontWeight={index === activeStep ? 'bold' : 'normal'}>
                  {status.label}
                </Typography>
              </StepLabel>
            </Step>
          ))}
        </Stepper>

        <Typography variant="body2" color="text.secondary" sx={{ textAlign: 'center' }}>
          {currentStatusConfig?.description}
        </Typography>
      </Paper>

      {/* Доступные действия */}
      {canManageDefects && availableTransitions.length > 0 && (
        <Paper elevation={2} sx={{ p: 3, mb: 2 }}>
          <Typography variant="h6" fontWeight="bold" mb={2}>
            Доступные действия
          </Typography>
          <Box display="flex" gap={2} flexWrap="wrap">
            {availableTransitions.map(statusKey => {
              const statusConfig = DEFECT_STATUSES.find(s => s.key === statusKey);
              if (!statusConfig) return null;

              return (
                <Button
                  key={statusKey}
                  variant="contained"
                  color={statusConfig.color}
                  startIcon={statusConfig.icon}
                  onClick={() => handleStatusChangeRequest(statusKey)}
                  size="medium"
                  sx={{ minWidth: 150 }}
                >
                  {getStatusActionLabel(statusKey)}
                </Button>
              );
            })}
          </Box>
        </Paper>
      )}

      {/* История изменений */}
      <Paper elevation={2} sx={{ p: 3 }}>
        <Box display="flex" alignItems="center" gap={1} mb={3}>
          <History color="primary" />
          <Typography variant="h6" fontWeight="bold">
            История изменений
          </Typography>
        </Box>
        
        <Timeline position="right">
          {/* Создание дефекта */}
          <TimelineItem>
            <TimelineOppositeContent color="text.secondary" variant="caption">
              {new Date(defect.created_at).toLocaleString('ru-RU')}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineDot color="info">
                <Assignment />
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="body2" fontWeight="bold">
                Дефект создан
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Создан пользователем {defect.reporter?.first_name} {defect.reporter?.last_name}
              </Typography>
            </TimelineContent>
          </TimelineItem>

          {/* Назначение исполнителя */}
          {defect.assignee && (
            <TimelineItem>
              <TimelineOppositeContent color="text.secondary" variant="caption">
                {new Date(defect.updated_at).toLocaleString('ru-RU')}
              </TimelineOppositeContent>
              <TimelineSeparator>
                <TimelineDot color="primary">
                  <PersonIcon />
                </TimelineDot>
                <TimelineConnector />
              </TimelineSeparator>
              <TimelineContent>
                <Typography variant="body2" fontWeight="bold">
                  Назначен исполнитель
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {defect.assignee.first_name} {defect.assignee.last_name}
                </Typography>
              </TimelineContent>
            </TimelineItem>
          )}

          {/* Текущий статус */}
          <TimelineItem>
            <TimelineOppositeContent color="text.secondary" variant="caption">
              {new Date(defect.updated_at).toLocaleString('ru-RU')}
            </TimelineOppositeContent>
            <TimelineSeparator>
              <TimelineDot color={currentStatusConfig?.color as any || 'primary'}>
                {currentStatusConfig?.icon}
              </TimelineDot>
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="body2" fontWeight="bold">
                {currentStatusConfig?.label || defect.status}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Текущий статус
              </Typography>
            </TimelineContent>
          </TimelineItem>

          {/* История из API (если есть) */}
          {statusHistory.map((historyItem, index) => (
            <TimelineItem key={index}>
              <TimelineOppositeContent color="text.secondary" variant="caption">
                {new Date(historyItem.changed_at).toLocaleString('ru-RU')}
              </TimelineOppositeContent>
              <TimelineSeparator>
                <TimelineDot>
                  <CommentIcon />
                </TimelineDot>
                {index < statusHistory.length - 1 && <TimelineConnector />}
              </TimelineSeparator>
              <TimelineContent>
                <Typography variant="body2" fontWeight="bold">
                  {historyItem.action}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {historyItem.user?.first_name} {historyItem.user?.last_name}
                </Typography>
                {historyItem.comment && (
                  <Typography variant="body2" sx={{ mt: 0.5 }}>
                    {historyItem.comment}
                  </Typography>
                )}
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      </Paper>

      {/* Диалог подтверждения изменения статуса */}
      <Dialog
        open={dialogOpen}
        onClose={() => setDialogOpen(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          Изменение статуса дефекта
        </DialogTitle>
        <DialogContent>
          <Box mb={2}>
            <Typography variant="body1" gutterBottom>
              Вы уверены, что хотите изменить статус дефекта на:
            </Typography>
            <Chip
              label={DEFECT_STATUSES.find(s => s.key === selectedStatus)?.label}
              color={DEFECT_STATUSES.find(s => s.key === selectedStatus)?.color}
              variant="outlined"
              size="medium"
            />
          </Box>
          
          <TextField
            label="Комментарий (необязательно)"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            fullWidth
            multiline
            rows={3}
            placeholder="Добавьте комментарий к изменению статуса..."
            sx={{ mt: 2 }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} disabled={loading}>
            Отмена
          </Button>
          <Button
            onClick={handleConfirmStatusChange}
            variant="contained"
            disabled={loading}
          >
            {loading ? 'Изменение...' : 'Подтвердить'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default DefectWorkflow;