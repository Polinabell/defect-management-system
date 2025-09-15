/**
 * Карточка дефекта для мобильного отображения
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Chip,
  Box,
  Avatar,
  IconButton,
  Menu,
  MenuItem,
  LinearProgress,
  Badge
} from '@mui/material';
import {
  MoreVert as MoreVertIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  AttachFile as AttachFileIcon,
  Comment as CommentIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Assignment as AssignIcon
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

interface DefectCardProps {
  defect: any;
  onClick: () => void;
  onEdit?: () => void;
  onAssign?: () => void;
  onStatusChange?: () => void;
}

export const DefectCard: React.FC<DefectCardProps> = ({
  defect,
  onClick,
  onEdit,
  onAssign,
  onStatusChange
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    event.stopPropagation();
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const getStatusColor = (status: string) => {
    const colors: { [key: string]: any } = {
      'new': 'info',
      'in_progress': 'warning',
      'review': 'secondary',
      'closed': 'success',
      'cancelled': 'error'
    };
    return colors[status] || 'default';
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

  const getProgressValue = (status: string) => {
    const progress: { [key: string]: number } = {
      'new': 20,
      'in_progress': 50,
      'review': 80,
      'closed': 100,
      'cancelled': 0
    };
    return progress[status] || 0;
  };

  const isOverdue = defect.due_date && new Date(defect.due_date) < new Date();

  return (
    <Card
      sx={{
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: 4
        },
        border: isOverdue ? '2px solid' : '1px solid',
        borderColor: isOverdue ? 'error.main' : 'divider',
        position: 'relative'
      }}
      onClick={onClick}
    >
      {/* Индикатор приоритета */}
      <Box
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: 4,
          backgroundColor: getPriorityColor(defect.priority)
        }}
      />

      <CardContent sx={{ pb: 1 }}>
        {/* Заголовок и номер */}
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={1}>
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ display: 'block' }}
            >
              #{defect.defect_number}
            </Typography>
            <Typography
              variant="h6"
              component="h3"
              sx={{
                fontWeight: 'bold',
                fontSize: '1rem',
                lineHeight: 1.2,
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical'
              }}
            >
              {defect.title}
            </Typography>
          </Box>

          <Box display="flex" alignItems="center" gap={0.5}>
            {isOverdue && (
              <WarningIcon color="error" fontSize="small" />
            )}
            <IconButton
              size="small"
              onClick={handleMenuOpen}
              sx={{ ml: 1 }}
            >
              <MoreVertIcon />
            </IconButton>
          </Box>
        </Box>

        {/* Статус и приоритет */}
        <Box display="flex" gap={1} mb={2} flexWrap="wrap">
          <Chip
            label={getStatusLabel(defect.status)}
            color={getStatusColor(defect.status)}
            size="small"
            variant="filled"
          />
          <Chip
            label={defect.priority}
            size="small"
            variant="outlined"
            sx={{
              borderColor: getPriorityColor(defect.priority),
              color: getPriorityColor(defect.priority)
            }}
          />
          {defect.category && (
            <Chip
              label={defect.category}
              size="small"
              variant="outlined"
              color="default"
            />
          )}
        </Box>

        {/* Прогресс */}
        <Box mb={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
            <Typography variant="caption" color="text.secondary">
              Прогресс
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {getProgressValue(defect.status)}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={getProgressValue(defect.status)}
            sx={{
              height: 6,
              borderRadius: 3,
              backgroundColor: 'grey.200',
              '& .MuiLinearProgress-bar': {
                borderRadius: 3,
                backgroundColor: getPriorityColor(defect.priority)
              }
            }}
          />
        </Box>

        {/* Описание */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 2,
            WebkitBoxOrient: 'vertical',
            mb: 2
          }}
        >
          {defect.description}
        </Typography>

        {/* Исполнитель */}
        {defect.assignee && (
          <Box display="flex" alignItems="center" gap={1} mb={1}>
            <Avatar sx={{ width: 24, height: 24 }}>
              <PersonIcon sx={{ fontSize: 16 }} />
            </Avatar>
            <Typography variant="caption" color="text.secondary">
              {defect.assignee.first_name} {defect.assignee.last_name}
            </Typography>
          </Box>
        )}

        {/* Даты */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          <Typography variant="caption" color="text.secondary">
            Создан: {formatDistanceToNow(new Date(defect.created_at), {
              addSuffix: true,
              locale: ru
            })}
          </Typography>
        </Box>

        {defect.due_date && (
          <Box display="flex" alignItems="center" gap={0.5}>
            <ScheduleIcon
              sx={{
                fontSize: 14,
                color: isOverdue ? 'error.main' : 'text.secondary'
              }}
            />
            <Typography
              variant="caption"
              color={isOverdue ? 'error.main' : 'text.secondary'}
              fontWeight={isOverdue ? 'bold' : 'normal'}
            >
              Срок: {new Date(defect.due_date).toLocaleDateString('ru-RU')}
            </Typography>
          </Box>
        )}
      </CardContent>

      <CardActions sx={{ pt: 0, justifyContent: 'space-between' }}>
        {/* Статистика */}
        <Box display="flex" gap={2}>
          {defect.attachments_count > 0 && (
            <Box display="flex" alignItems="center" gap={0.5}>
              <AttachFileIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {defect.attachments_count}
              </Typography>
            </Box>
          )}
          
          {defect.comments_count > 0 && (
            <Box display="flex" alignItems="center" gap={0.5}>
              <CommentIcon sx={{ fontSize: 16, color: 'text.secondary' }} />
              <Typography variant="caption" color="text.secondary">
                {defect.comments_count}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Проект */}
        {defect.project && (
          <Typography variant="caption" color="primary.main" fontWeight="medium">
            {defect.project.name}
          </Typography>
        )}
      </CardActions>

      {/* Меню действий */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        onClick={(e) => e.stopPropagation()}
      >
        <MenuItem
          onClick={() => {
            onClick();
            handleMenuClose();
          }}
        >
          <ViewIcon sx={{ mr: 1 }} />
          Просмотр
        </MenuItem>
        
        {onEdit && (
          <MenuItem
            onClick={() => {
              onEdit();
              handleMenuClose();
            }}
          >
            <EditIcon sx={{ mr: 1 }} />
            Редактировать
          </MenuItem>
        )}
        
        {onAssign && (
          <MenuItem
            onClick={() => {
              onAssign();
              handleMenuClose();
            }}
          >
            <AssignIcon sx={{ mr: 1 }} />
            Назначить
          </MenuItem>
        )}
        
        {onStatusChange && (
          <MenuItem
            onClick={() => {
              onStatusChange();
              handleMenuClose();
            }}
          >
            <ScheduleIcon sx={{ mr: 1 }} />
            Изменить статус
          </MenuItem>
        )}
      </Menu>
    </Card>
  );
};
