/**
 * Компонент для перехвата ошибок React
 */

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Alert } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  private handleReload = () => {
    window.location.reload();
  };

  public render() {
    if (this.state.hasError) {
      return (
        <Box
          display="flex"
          flexDirection="column"
          alignItems="center"
          justifyContent="center"
          minHeight="50vh"
          padding={3}
        >
          <Alert severity="error" sx={{ mb: 3, maxWidth: 600 }}>
            <Typography variant="h6" gutterBottom>
              Произошла ошибка приложения
            </Typography>
            <Typography variant="body2" gutterBottom>
              {this.state.error?.message || 'Неизвестная ошибка'}
            </Typography>
          </Alert>
          
          <Button
            variant="contained"
            startIcon={<RefreshIcon />}
            onClick={this.handleReload}
            color="primary"
          >
            Перезагрузить страницу
          </Button>
          
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <Box mt={3} p={2} bgcolor="grey.100" borderRadius={1} maxWidth={800}>
              <Typography variant="caption" component="pre" style={{ whiteSpace: 'pre-wrap' }}>
                {this.state.error.stack}
              </Typography>
            </Box>
          )}
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;