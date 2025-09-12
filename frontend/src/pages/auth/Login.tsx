/**
 * Страница входа в систему
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  Container,
  CircularProgress
} from '@mui/material';
import { useAuth } from '../../contexts/AuthContext.tsx';
import { useNotification } from '../../contexts/NotificationContext.tsx';

export const Login: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loading } = useAuth();
  const { showSuccess } = useNotification();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!username || !password) {
      setError('Пожалуйста, заполните все поля');
      return;
    }

    const success = await login(username, password);
    if (success) {
      showSuccess('Вход выполнен успешно!');
    } else {
      setError('Неверные учетные данные');
    }
  };

  return (
    <Container maxWidth="sm">
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        justifyContent="center"
        minHeight="100vh"
      >
        <Card sx={{ width: '100%', maxWidth: 400 }}>
          <CardContent sx={{ p: 4 }}>
            <Typography variant="h4" component="h1" align="center" gutterBottom>
              Вход в систему
            </Typography>
            
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
              Система управления дефектами
            </Typography>

            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit}>
              <TextField
                fullWidth
                label="Имя пользователя"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                margin="normal"
                required
                disabled={loading}
              />
              
              <TextField
                fullWidth
                label="Пароль"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                margin="normal"
                required
                disabled={loading}
              />

              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ mt: 3, mb: 2 }}
                disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Войти'}
              </Button>
            </Box>

            <Alert severity="info" sx={{ mt: 2 }}>
              <Typography variant="body2" component="div">
                <strong>Демо пользователи (пароль: password):</strong><br />
                • manager - Менеджер проектов<br />
                • engineer - Инженер<br />
                • observer - Наблюдатель
              </Typography>
            </Alert>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};