/**
 * Центр уведомлений
 */

import React, { useState, useEffect } from 'react';
import {
  IconButton,
  Badge,
  Popover,
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Button,
  Divider,
  Tab,
  Tabs,
  Paper,
  ListItemSecondaryAction,
  Tooltip,
  Alert
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  NotificationsOff as NotificationsOffIcon,
  Circle as CircleIcon,
  BugReport as DefectIcon,
  Assignment as ProjectIcon,
  Person as PersonIcon,
  Schedule as ScheduleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  Clear as ClearIcon,
  MarkEmailRead as MarkReadIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';
import { useNavigate } from 'react-router-dom';

interface Notification {
  id: number;
  type: 'defect' | 'project' | 'user' | 'system';
  priority: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  message: string;
  created_at: string;
  read: boolean;
  action_url?: string;
  data?: any;
}

interface NotificationCenterProps {
  onNotificationClick?: (notification: Notification) => void;
}

export const NotificationCenter: React.FC<NotificationCenterProps> = ({
  onNotificationClick
}) => {
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<HTMLButtonElement | null>(null);
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [tabValue, setTabValue] = useState(0);
  const [loading, setLoading] = useState(false);

  // Загрузка уведомлений при монтировании
  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    setLoading(true);
    try {
      // Здесь должен быть запрос к API
      // const response = await notificationsAPI.getNotifications();
      // setNotifications(response.results);
      
      // Мок данные
      const mockNotifications: Notification[] = [
        {
          id: 1,
          type: 'defect',
          priority: 'high',
          title: 'Новый критический дефект',
          message: 'Дефект #DEF-001 "Проблема с водоснабжением" требует немедленного внимания',
          created_at: new Date(Date.now() - 30 * 60 * 1000).toISOString(), // 30 минут назад
          read: false,
          action_url: '/defects/1'
        },
        {
          id: 2,
          type: 'defect',
          priority: 'medium',
          title: 'Дефект назначен вам',
          message: 'Вам назначен дефект #DEF-002 "Треск в стене"',
          created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 часа назад
          read: false,
          action_url: '/defects/2'
        },
        {
          id: 3,
          type: 'defect',
          priority: 'high',
          title: 'Приближается срок',
          message: 'Дефект #DEF-003 "Неисправность лифта" должен быть исправлен до завтра',
          created_at: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 часа назад
          read: true,
          action_url: '/defects/3'
        },
        {
          id: 4,
          type: 'project',
          priority: 'medium',
          title: 'Обновление проекта',
          message: 'Проект "Жилой комплекс Парк" обновлен',
          created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 день назад
          read: true,
          action_url: '/projects/1'
        },
        {
          id: 5,
          type: 'system',
          priority: 'low',
          title: 'Системное обновление',
          message: 'Система будет недоступна с 02:00 до 04:00 для планового обслуживания',
          created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 дня назад
          read: true
        }
      ];
      
      setNotifications(mockNotifications);
    } catch (error) {
      console.error('Ошибка загрузки уведомлений:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const markAsRead = async (notificationId: number) => {
    try {
      // await notificationsAPI.markAsRead(notificationId);
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, read: true } : n)
      );
    } catch (error) {
      console.error('Ошибка при отметке как прочитанное:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      // await notificationsAPI.markAllAsRead();
      setNotifications(prev => prev.map(n => ({ ...n, read: true })));
    } catch (error) {
      console.error('Ошибка при отметке всех как прочитанные:', error);
    }
  };

  const deleteNotification = async (notificationId: number) => {
    try {
      // await notificationsAPI.deleteNotification(notificationId);
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (error) {
      console.error('Ошибка удаления уведомления:', error);
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      markAsRead(notification.id);
    }
    
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
    
    handleClose();
  };

  const getNotificationIcon = (type: string, priority: string) => {
    const iconProps = {
      fontSize: 'small' as const,
      color: (priority === 'critical' ? 'error' :
             priority === 'high' ? 'warning' :
             priority === 'medium' ? 'info' : 'action') as any
    };

    switch (type) {
      case 'defect':
        return <DefectIcon {...iconProps} />;
      case 'project':
        return <ProjectIcon {...iconProps} />;
      case 'user':
        return <PersonIcon {...iconProps} />;
      case 'system':
        return <InfoIcon {...iconProps} />;
      default:
        return <NotificationsIcon {...iconProps} />;
    }
  };

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

  const unreadCount = notifications.filter(n => !n.read).length;
  const open = Boolean(anchorEl);

  // Фильтрация уведомлений по вкладкам
  const filteredNotifications = notifications.filter(notification => {
    switch (tabValue) {
      case 0: // Все
        return true;
      case 1: // Непрочитанные
        return !notification.read;
      case 2: // Дефекты
        return notification.type === 'defect';
      case 3: // Проекты
        return notification.type === 'project';
      default:
        return true;
    }
  });

  return (
    <>
      <Tooltip title="Уведомления">
        <IconButton color="inherit" onClick={handleClick}>
          <Badge badgeContent={unreadCount} color="error">
            {unreadCount > 0 ? <NotificationsIcon /> : <NotificationsOffIcon />}
          </Badge>
        </IconButton>
      </Tooltip>

      <Popover
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        PaperProps={{
          sx: { width: 400, maxHeight: 600 }
        }}
      >
        <Paper>
          {/* Заголовок */}
          <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Typography variant="h6" fontWeight="bold">
                Уведомления
              </Typography>
              <Box display="flex" gap={1}>
                {unreadCount > 0 && (
                  <Tooltip title="Отметить все как прочитанные">
                    <IconButton size="small" onClick={markAllAsRead}>
                      <MarkReadIcon />
                    </IconButton>
                  </Tooltip>
                )}
                <Tooltip title="Настройки уведомлений">
                  <IconButton
                    size="small"
                    onClick={() => {
                      handleClose();
                      navigate('/settings');
                    }}
                  >
                    <SettingsIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>

            {/* Счетчик */}
            {unreadCount > 0 && (
              <Typography variant="caption" color="text.secondary">
                {unreadCount} непрочитанных
              </Typography>
            )}
          </Box>

          {/* Вкладки */}
          <Tabs
            value={tabValue}
            onChange={handleTabChange}
            variant="scrollable"
            scrollButtons="auto"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label="Все" />
            <Tab label="Непрочитанные" />
            <Tab label="Дефекты" />
            <Tab label="Проекты" />
          </Tabs>

          {/* Список уведомлений */}
          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {filteredNotifications.length === 0 ? (
              <Box sx={{ p: 3, textAlign: 'center' }}>
                <NotificationsOffIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 1 }} />
                <Typography variant="body2" color="text.secondary">
                  {tabValue === 1 ? 'Нет непрочитанных уведомлений' : 'Нет уведомлений'}
                </Typography>
              </Box>
            ) : (
              <List disablePadding>
                {filteredNotifications.map((notification, index) => (
                  <React.Fragment key={notification.id}>
                    <ListItem
                      alignItems="flex-start"
                      sx={{
                        cursor: 'pointer',
                        backgroundColor: notification.read ? 'transparent' : 'action.hover',
                        '&:hover': {
                          backgroundColor: 'action.selected'
                        }
                      }}
                      onClick={() => handleNotificationClick(notification)}
                    >
                      <ListItemAvatar>
                        <Avatar
                          sx={{
                            width: 32,
                            height: 32,
                            bgcolor: notification.read ? 'grey.300' : 'primary.main'
                          }}
                        >
                          {getNotificationIcon(notification.type, notification.priority)}
                        </Avatar>
                      </ListItemAvatar>

                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography
                              variant="body2"
                              fontWeight={notification.read ? 'normal' : 'bold'}
                              sx={{ flexGrow: 1 }}
                            >
                              {notification.title}
                            </Typography>
                            <Chip
                              label={notification.priority}
                              size="small"
                              color={getPriorityColor(notification.priority) as any}
                              variant="outlined"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography
                              variant="body2"
                              color="text.secondary"
                              sx={{ mt: 0.5 }}
                            >
                              {notification.message}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {formatDistanceToNow(new Date(notification.created_at), {
                                addSuffix: true,
                                locale: ru
                              })}
                            </Typography>
                          </Box>
                        }
                      />

                      <ListItemSecondaryAction>
                        <Box display="flex" flexDirection="column" alignItems="center" gap={1}>
                          {!notification.read && (
                            <CircleIcon sx={{ fontSize: 8, color: 'primary.main' }} />
                          )}
                          <Tooltip title="Удалить">
                            <IconButton
                              size="small"
                              onClick={(e) => {
                                e.stopPropagation();
                                deleteNotification(notification.id);
                              }}
                            >
                              <ClearIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </ListItemSecondaryAction>
                    </ListItem>
                    
                    {index < filteredNotifications.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            )}
          </Box>

          {/* Футер */}
          {filteredNotifications.length > 0 && (
            <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
              <Button
                fullWidth
                variant="outlined"
                size="small"
                onClick={() => {
                  handleClose();
                  navigate('/notifications');
                }}
              >
                Посмотреть все уведомления
              </Button>
            </Box>
          )}
        </Paper>
      </Popover>
    </>
  );
};
