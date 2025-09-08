/**
 * Главный компонент приложения
 */

import React from 'react';
import { BrowserRouter as Router } from 'react-router-dom';
import { Provider } from 'react-redux';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { QueryClient, QueryClientProvider } from 'react-query';
import { SnackbarProvider } from 'notistack';
import { HelmetProvider } from 'react-helmet-async';

import { store } from './store';
import { theme } from './theme';
import { AppRoutes } from './routes';
import { AuthProvider } from './contexts/AuthContext';
import { LoadingProvider } from './contexts/LoadingContext';
import { NotificationProvider } from './contexts/NotificationContext';
import ErrorBoundary from './components/common/ErrorBoundary';

// Настройка React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 2,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 минут
    },
  },
});

const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <HelmetProvider>
        <Provider store={store}>
          <QueryClientProvider client={queryClient}>
            <ThemeProvider theme={theme}>
              <CssBaseline />
              <SnackbarProvider
                maxSnack={3}
                anchorOrigin={{
                  vertical: 'top',
                  horizontal: 'right',
                }}
                autoHideDuration={5000}
              >
                <Router>
                  <AuthProvider>
                    <LoadingProvider>
                      <NotificationProvider>
                        <AppRoutes />
                      </NotificationProvider>
                    </LoadingProvider>
                  </AuthProvider>
                </Router>
              </SnackbarProvider>
            </ThemeProvider>
          </QueryClientProvider>
        </Provider>
      </HelmetProvider>
    </ErrorBoundary>
  );
};

export default App;
