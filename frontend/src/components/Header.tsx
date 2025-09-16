import React from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Avatar,
  Menu,
  MenuItem,
  IconButton,
} from '@mui/material';
import { AccountCircle, Notifications, Settings } from '@mui/icons-material';
import { useAppDispatch, useAppSelector } from '../hooks/redux';
import { logout } from '../store/slices/authSlice';

const Header: React.FC = () => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated } = useAppSelector((state) => state.auth);
  const [anchorEl, setAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    dispatch(logout());
    handleClose();
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          🏗️ Система управления дефектами
        </Typography>
        
        {isAuthenticated ? (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton color="inherit">
              <Notifications />
            </IconButton>
            
            <IconButton color="inherit">
              <Settings />
            </IconButton>
            
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <Avatar sx={{ bgcolor: 'secondary.main' }}>
                {user?.first_name?.charAt(0) || user?.email?.charAt(0) || 'U'}
              </Avatar>
            </IconButton>
            
            <Menu
              id="menu-appbar"
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
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={handleClose}>
                <AccountCircle sx={{ mr: 1 }} />
                Профиль
              </MenuItem>
              <MenuItem onClick={handleLogout}>
                Выйти
              </MenuItem>
            </Menu>
            
            <Typography variant="body2" sx={{ ml: 1 }}>
              {user?.first_name || user?.email}
            </Typography>
          </Box>
        ) : (
          <Button color="inherit">
            Войти
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
};

export default Header;

