import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box, Toolbar } from '@mui/material';
import { Provider } from 'react-redux';
import { store } from './store';
import theme from './theme';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import DefectsPage from './pages/DefectsPage';

function App() {
  const [sidebarOpen, setSidebarOpen] = React.useState(true);

  const handleSidebarClose = () => {
    setSidebarOpen(false);
  };

  return (
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Router>
          <Box sx={{ display: 'flex' }}>
            <Header />
            <Sidebar open={sidebarOpen} onClose={handleSidebarClose} />
            
            <Box
              component="main"
              sx={{
                flexGrow: 1,
                p: 3,
                width: { sm: `calc(100% - 240px)` },
                ml: { sm: '240px' },
              }}
            >
              <Toolbar />
              
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard" element={<HomePage />} />
                <Route path="/defects" element={<DefectsPage />} />
                <Route path="/projects" element={
                  <Box sx={{ p: 3, textAlign: 'center' }}>
                    <h2>🏢 Проекты (в разработке)</h2>
                    <p>Страница управления проектами будет добавлена позже.</p>
                  </Box>
                } />
                <Route path="/reports" element={
                  <Box sx={{ p: 3, textAlign: 'center' }}>
                    <h2>📊 Отчёты (в разработке)</h2>
                    <p>Страница отчётов будет добавлена позже.</p>
                  </Box>
                } />
                <Route path="/users" element={
                  <Box sx={{ p: 3, textAlign: 'center' }}>
                    <h2>👥 Пользователи (в разработке)</h2>
                    <p>Страница управления пользователями будет добавлена позже.</p>
                  </Box>
                } />
              </Routes>
            </Box>
          </Box>
        </Router>
      </ThemeProvider>
    </Provider>
  );
}

export default App;