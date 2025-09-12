/**
 * Компонент управления workflow дефектов
 */

import React from 'react';
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
} from '@mui/material';
import {
  PlayArrow,
  Visibility,
  Check,
  Close,
  History,
  Assignment,
} from '@mui/icons-material';
import { Defect } from '../../types';

interface DefectWorkflowProps {
  defect: Defect;
  onStatusChange: (defectId: number, newStatus: string) => void;
  canManageDefects?: boolean;
}

const DEFECT_STATUSES = [
  { key: 'new', label: 'Новый', icon: <Assignment />, color: 'info' as const },
  { key: 'in_progress', label: 'В работе', icon: <PlayArrow />, color: 'primary' as const },
  { key: 'review', label: 'На проверке', icon: <Visibility />, color: 'warning' as const },
  { key: 'closed', label: 'Закрыт', icon: <Check />, color: 'success' as const },
  { key: 'cancelled', label: 'Отменён', icon: <Close />, color: 'error' as const },
];

const getStatusIndex = (status: string) => {
  const index = DEFECT_STATUSES.findIndex(s => s.key === status);
  return index === -1 ? 0 : index;
};

const getAvailableTransitions = (currentStatus: string) => {
  switch (currentStatus) {
    case 'new':
      return ['in_progress', 'cancelled'];
    case 'in_progress':
      return ['review', 'cancelled'];
    case 'review':
      return ['closed', 'in_progress', 'cancelled'];
    case 'closed':
      return ['in_progress']; // переоткрытие
    case 'cancelled':
      return ['new']; // восстановление
    default:
      return [];
  }
};

export const DefectWorkflow: React.FC<DefectWorkflowProps> = ({
  defect,
  onStatusChange,
  canManageDefects = false,
}) => {
  const activeStep = getStatusIndex(defect.status);
  const availableTransitions = getAvailableTransitions(defect.status);
  const currentStatusConfig = DEFECT_STATUSES.find(s => s.key === defect.status);

  const handleStatusChange = (newStatus: string) => {
    onStatusChange(defect.id, newStatus);
  };

  return (
    <Box>
      <Paper elevation={2} sx={{ p: 2, mb: 2 }}>
        <Box display="flex" alignItems="center" gap={2} mb={2}>
          <Typography variant="h6">
            Workflow дефекта #{defect.id}
          </Typography>
          <Chip
            icon={currentStatusConfig?.icon}
            label={currentStatusConfig?.label || defect.status}
            color={currentStatusConfig?.color || 'default'}
            variant="filled"
          />
        </Box>

        <Stepper activeStep={activeStep} orientation="vertical">
          {DEFECT_STATUSES.filter(s => !['cancelled'].includes(s.key)).map((status, index) => (
            <Step key={status.key} completed={index < activeStep}>
              <StepLabel
                icon={status.icon}
                optional={
                  status.key === defect.status ? (
                    <Typography variant="caption" color="primary">
                      Текущий статус
                    </Typography>
                  ) : undefined
                }
              >
                {status.label}
              </StepLabel>
              <StepContent>
                <Typography variant="body2" color="text.secondary">
                  {status.key === 'new' && 'Дефект зарегистрирован и ожидает назначения исполнителя'}
                  {status.key === 'in_progress' && 'Дефект находится в работе у исполнителя'}
                  {status.key === 'review' && 'Дефект на проверке у ответственного'}
                  {status.key === 'closed' && 'Дефект успешно исправлен и закрыт'}
                </Typography>
              </StepContent>
            </Step>
          ))}
        </Stepper>
      </Paper>

      {canManageDefects && availableTransitions.length > 0 && (
        <Paper elevation={2} sx={{ p: 2 }}>
          <Typography variant="h6" mb={2}>
            Доступные действия
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap">
            {availableTransitions.map(statusKey => {
              const statusConfig = DEFECT_STATUSES.find(s => s.key === statusKey);
              if (!statusConfig) return null;

              return (
                <Button
                  key={statusKey}
                  variant="outlined"
                  color={statusConfig.color}
                  startIcon={statusConfig.icon}
                  onClick={() => handleStatusChange(statusKey)}
                  size="small"
                >
                  {statusKey === 'in_progress' && defect.status === 'closed' ? 'Переоткрыть' :
                   statusKey === 'new' && defect.status === 'cancelled' ? 'Восстановить' :
                   `Перевести в "${statusConfig.label}"`}
                </Button>
              );
            })}
          </Box>
        </Paper>
      )}

      {/* История изменений статусов */}
      <Paper elevation={2} sx={{ p: 2, mt: 2 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <History />
          <Typography variant="h6">
            История изменений
          </Typography>
        </Box>
        
        <Box>
          {/* Пример истории - в реальном проекте данные из API */}
          <Box display="flex" alignItems="center" gap={2} py={1}>
            <Typography variant="body2" color="text.secondary">
              {new Date(defect.created_at).toLocaleString()}
            </Typography>
            <Chip size="small" label="Создан" color="info" />
            <Typography variant="body2">
              Создан пользователем {defect.reporter?.first_name} {defect.reporter?.last_name}
            </Typography>
          </Box>
          
          {defect.assignee && (
            <Box display="flex" alignItems="center" gap={2} py={1}>
              <Typography variant="body2" color="text.secondary">
                {new Date(defect.updated_at).toLocaleString()}
              </Typography>
              <Chip size="small" label="Назначен" color="primary" />
              <Typography variant="body2">
                Назначен на {defect.assignee.first_name} {defect.assignee.last_name}
              </Typography>
            </Box>
          )}
          
          <Box display="flex" alignItems="center" gap={2} py={1}>
            <Typography variant="body2" color="text.secondary">
              {new Date(defect.updated_at).toLocaleString()}
            </Typography>
            <Chip 
              size="small" 
              label={currentStatusConfig?.label || defect.status}
              color={currentStatusConfig?.color || 'default'}
            />
            <Typography variant="body2">
              Текущий статус
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default DefectWorkflow;