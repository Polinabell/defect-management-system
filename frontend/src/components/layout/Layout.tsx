/**
 * Основной макет приложения с навигацией
 */

import React, { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Button,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  Divider,
  Badge,
  Tooltip,
  useTheme,
  useMediaQuery
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  BugReport as DefectsIcon,
  Assignment as ProjectsIcon,
  Assessment as ReportsIcon,
  People as UsersIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  AccountCircle as AccountIcon,
  Logout as LogoutIcon,
  ChevronLeft as ChevronLeftIcon,
  DarkMode as DarkModeIcon,
  LightMode as LightModeIcon
} from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { NotificationCenter } from '../notifications/NotificationCenter';
import { usePermissions } from '../common/RoleGuard';
import { useTheme as useCustomTheme } from '../../contexts/ThemeContext';

const drawerWidth = 280;

const navigationItems = [
  {
    text: 'Дашборд',
    icon: <DashboardIcon />,
    path: '/dashboard',
    roles: ['manager', 'engineer', 'observer']
  },
  {
    text: 'Дефекты',
    icon: <DefectsIcon />,
    path: '/defects',
    roles: ['manager', 'engineer', 'observer']
  },
  {
    text: 'Проекты',
    icon: <ProjectsIcon />,
    path: '/projects',
    roles: ['manager', 'engineer', 'observer']
  },
  {
    text: 'Отчеты',
    icon: <ReportsIcon />,
    path: '/reports',
    roles: ['manager', 'engineer', 'observer']
  },
  {
    text: 'Пользователи',
    icon: <UsersIcon />,
    path: '/users',
    roles: ['manager']
  }
];

export const Layout: React.FC = () => {
  const { logout, user, hasPermission } = useAuth();
  const permissions = usePermissions();
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const { mode, toggleTheme } = useCustomTheme();

  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuAnchorEl, setUserMenuAnchorEl] = useState<null | HTMLElement>(null);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchorEl(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchorEl(null);
  };

  const handleNavigate = (path: string) => {
    navigate(path);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const filteredNavigationItems = navigationItems.filter(item => {
    if (item.path === '/users') {
      return permissions.canManageUsers();
    }
    return item.roles.includes(user?.role || '');
  });

  const drawer = (
    <Box>
      {/* Logo */}
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Avatar sx={{ bgcolor: 'primary.main' }}>
          <DefectsIcon />
        </Avatar>
        <Typography variant="h6" noWrap fontWeight="bold">
          DMS
        </Typography>
        {!isMobile && (
          <IconButton onClick={handleDrawerToggle} sx={{ ml: 'auto' }}>
            <ChevronLeftIcon />
          </IconButton>
        )}
      </Box>

      <Divider />

      {/* Navigation */}
      <List sx={{ px: 1 }}>
        {filteredNavigationItems.map((item) => {
          const isActive = location.pathname === item.path || 
                          (item.path === '/defects' && location.pathname.startsWith('/defects/'));
          
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => handleNavigate(item.path)}
                selected={isActive}
                sx={{
                  borderRadius: 2,
                  mx: 1,
                  '&.Mui-selected': {
                    backgroundColor: 'primary.main',
                    color: 'primary.contrastText',
                    '&:hover': {
                      backgroundColor: 'primary.dark',
                    },
                    '& .MuiListItemIcon-root': {
                      color: 'primary.contrastText',
                    }
                  }
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText 
                  primary={item.text}
                  primaryTypographyProps={{
                    fontWeight: isActive ? 'bold' : 'normal'
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Divider sx={{ mt: 'auto' }} />

      {/* User Info */}
      <Box sx={{ p: 2 }}>
        <Box
          sx={{
            display: 'flex',
            alignItems: 'center',
            gap: 2,
            p: 1,
            borderRadius: 2,
            backgroundColor: 'background.default',
            cursor: 'pointer'
          }}
          onClick={handleUserMenuOpen}
        >
          <Avatar sx={{ width: 32, height: 32 }}>
            <AccountIcon />
          </Avatar>
          <Box sx={{ flexGrow: 1, minWidth: 0 }}>
            <Typography variant="body2" noWrap fontWeight="medium">
              {user?.first_name} {user?.last_name}
            </Typography>
            <Typography variant="caption" color="text.secondary" noWrap>
              {user?.role === 'manager' ? 'Менеджер' :
               user?.role === 'engineer' ? 'Инженер' : 'Наблюдатель'}
            </Typography>
            {/* Индикатор прав доступа */}
            <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
              {permissions.canCreate() && (
                <Tooltip title="Может создавать дефекты">
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: 'success.main'
                    }}
                  />
                </Tooltip>
              )}
              {permissions.canManageUsers() && (
                <Tooltip title="Может управлять пользователями">
                  <Box
                    sx={{
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      bgcolor: 'primary.main'
                    }}
                  />
                </Tooltip>
              )}
            </Box>
          </Box>
        </Box>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* App Bar */}
      <AppBar
        position="fixed"
        sx={{
          width: { md: `calc(100% - ${drawerWidth}px)` },
          ml: { md: `${drawerWidth}px` },
          zIndex: theme.zIndex.drawer + 1
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { md: 'none' } }}
          >
            <MenuIcon />
          </IconButton>

          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Система управления дефектами
          </Typography>

          {/* Theme Toggle */}
          <Tooltip title={mode === 'light' ? 'Переключить на темную тему' : 'Переключить на светлую тему'}>
            <IconButton
              color="inherit"
              onClick={toggleTheme}
              sx={{ ml: 1 }}
            >
              {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
            </IconButton>
          </Tooltip>

          {/* Notifications */}
          <NotificationCenter onNotificationClick={(notification) => {
            if (notification.action_url) {
              navigate(notification.action_url);
            }
          }} />

          {/* User Avatar */}
          <Tooltip title="Профиль пользователя">
            <IconButton
              color="inherit"
              onClick={handleUserMenuOpen}
              sx={{ ml: 1 }}
            >
              <Avatar sx={{ width: 32, height: 32 }}>
                <AccountIcon />
              </Avatar>
            </IconButton>
          </Tooltip>
        </Toolbar>
      </AppBar>

      {/* Navigation Drawer */}
      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {/* Mobile drawer */}
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
          sx={{
            display: { xs: 'block', md: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              height: '100vh'
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Desktop drawer */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', md: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              height: '100vh',
              borderRight: '1px solid',
              borderColor: 'divider'
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { md: `calc(100% - ${drawerWidth}px)` },
          minHeight: '100vh',
          backgroundColor: 'background.default'
        }}
      >
        <Toolbar /> {/* Spacer for AppBar */}
        <Box sx={{ p: 3 }}>
          <Outlet />
        </Box>
      </Box>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchorEl}
        open={Boolean(userMenuAnchorEl)}
        onClose={handleUserMenuClose}
        PaperProps={{
          sx: { width: 200 }
        }}
      >
        <MenuItem disabled>
          <Box>
            <Typography variant="body2" fontWeight="medium">
              {user?.first_name} {user?.last_name}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {user?.email}
            </Typography>
          </Box>
        </MenuItem>
        
        <Divider />
        
        <MenuItem onClick={() => {
          handleUserMenuClose();
          navigate('/profile');
        }}>
          <AccountIcon sx={{ mr: 2 }} />
          Профиль
        </MenuItem>

        <MenuItem onClick={() => {
          handleUserMenuClose();
          navigate('/settings');
        }}>
          <SettingsIcon sx={{ mr: 2 }} />
          Настройки
        </MenuItem>

        <MenuItem onClick={() => {
          handleUserMenuClose();
          toggleTheme();
        }}>
          {mode === 'light' ? <DarkModeIcon sx={{ mr: 2 }} /> : <LightModeIcon sx={{ mr: 2 }} />}
          {mode === 'light' ? 'Темная тема' : 'Светлая тема'}
        </MenuItem>

        <Divider />
        
        <MenuItem 
          onClick={() => {
            handleUserMenuClose();
            logout();
          }}
          sx={{ color: 'error.main' }}
        >
          <LogoutIcon sx={{ mr: 2 }} />
          Выйти
        </MenuItem>
      </Menu>
    </Box>
  );
};