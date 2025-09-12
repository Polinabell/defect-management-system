/**
 * Страница отчетов
 */

import React from 'react';
import { Typography, Box, Paper, Grid, Button } from '@mui/material';
import { Download as DownloadIcon } from '@mui/icons-material';

export const Reports: React.FC = () => {
  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          Отчеты
        </Typography>
        <Button
          variant="contained"
          startIcon={<DownloadIcon />}
          color="primary"
        >
          Экспорт отчета
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Отчеты по дефектам
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Здесь будут графики и отчеты...
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};