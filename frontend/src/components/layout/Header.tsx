import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Tooltip,
  Button,
} from '@mui/material';
import {
  NotificationsOutlined as NotificationsIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';

interface HeaderProps {
  onMenuToggle?: () => void;
  showMenuButton?: boolean;
  title?: string;
}

export const Header: React.FC<HeaderProps> = ({
  onMenuToggle,
  showMenuButton = false,
  title = 'Система управления дефектами',
}) => {
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);
  const [notificationCount] = React.useState(3);

  const handleProfileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const isMenuOpen = Boolean(anchorEl);

  return (
    <>
      <AppBar position="sticky" elevation={1}>
        <Toolbar>
          {showMenuButton && (
            <IconButton
              edge="start"
              color="inherit"
              aria-label="menu"
              onClick={onMenuToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}

          <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>

          <Box display="flex" alignItems="center" gap={1}>
            <Tooltip title="Уведомления">
              <IconButton color="inherit">
                <Badge badgeContent={notificationCount} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>

            <Tooltip title="Настройки">
              <IconButton color="inherit">
                <SettingsIcon />
              </IconButton>
            </Tooltip>

            <Tooltip title="Профиль">
              <IconButton
                edge="end"
                aria-label="account"
                aria-controls="profile-menu"
                aria-haspopup="true"
                onClick={handleProfileMenuOpen}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                  <AccountIcon />
                </Avatar>
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      <Menu
        id="profile-menu"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={isMenuOpen}
        onClose={handleMenuClose}
      >
        <MenuItem onClick={handleMenuClose}>
          <AccountIcon sx={{ mr: 1 }} />
          Мой профиль
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          <SettingsIcon sx={{ mr: 1 }} />
          Настройки
        </MenuItem>
        <MenuItem onClick={handleMenuClose}>
          Выйти
        </MenuItem>
      </Menu>
    </>
  );
};

export default Header;