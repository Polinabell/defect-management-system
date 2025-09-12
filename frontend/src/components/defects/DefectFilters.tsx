/**
 * Компонент расширенной фильтрации дефектов
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  Grid,
  Collapse,
  IconButton,
  Autocomplete,
  FormControlLabel,
  Checkbox,
  Slider,
  Divider,
  Badge,
  Tooltip
} from '@mui/material';
import {
  Search as SearchIcon,
  FilterList as FilterIcon,
  Clear as ClearIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Save as SaveIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ru } from 'date-fns/locale';

interface DefectFiltersProps {
  filters: any;
  onFiltersChange: (filters: any) => void;
  projects: any[];
  users: any[];
  categories: string[];
  onSaveFilter?: (filterName: string, filters: any) => void;
  savedFilters?: Array<{ name: string; filters: any }>;
}

const priorityOptions = [
  { value: 'low', label: 'Низкий', color: '#4caf50' },
  { value: 'medium', label: 'Средний', color: '#ff9800' },
  { value: 'high', label: 'Высокий', color: '#f44336' },
  { value: 'critical', label: 'Критический', color: '#d32f2f' }
];

const statusOptions = [
  { value: 'new', label: 'Новый', color: '#2196f3' },
  { value: 'in_progress', label: 'В работе', color: '#ff9800' },
  { value: 'review', label: 'На проверке', color: '#9c27b0' },
  { value: 'closed', label: 'Закрыт', color: '#4caf50' },
  { value: 'cancelled', label: 'Отменен', color: '#f44336' }
];

const severityOptions = [
  { value: 'minor', label: 'Незначительный' },
  { value: 'major', label: 'Значительный' },
  { value: 'critical', label: 'Критический' },
  { value: 'blocker', label: 'Блокирующий' }
];

export const DefectFilters: React.FC<DefectFiltersProps> = ({
  filters,
  onFiltersChange,
  projects,
  users,
  categories,
  onSaveFilter,
  savedFilters = []
}) => {
  const [expanded, setExpanded] = useState(false);
  const [searchTerm, setSearchTerm] = useState(filters.search || '');
  const [saveDialogOpen, setSaveDialogOpen] = useState(false);
  const [filterName, setFilterName] = useState('');

  // Debounced search
  useEffect(() => {
    const timer = setTimeout(() => {
      onFiltersChange({ ...filters, search: searchTerm });
    }, 300);

    return () => clearTimeout(timer);
  }, [searchTerm]);

  const handleFilterChange = (key: string, value: any) => {
    onFiltersChange({ ...filters, [key]: value });
  };

  const clearAllFilters = () => {
    setSearchTerm('');
    onFiltersChange({
      search: '',
      project: [],
      status: [],
      priority: [],
      severity: [],
      category: [],
      assignee: [],
      reporter: [],
      created_after: null,
      created_before: null,
      due_after: null,
      due_before: null,
      is_overdue: false,
      has_attachments: false
    });
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.search) count++;
    if (filters.project?.length) count++;
    if (filters.status?.length) count++;
    if (filters.priority?.length) count++;
    if (filters.severity?.length) count++;
    if (filters.category?.length) count++;
    if (filters.assignee?.length) count++;
    if (filters.reporter?.length) count++;
    if (filters.created_after) count++;
    if (filters.created_before) count++;
    if (filters.due_after) count++;
    if (filters.due_before) count++;
    if (filters.is_overdue) count++;
    if (filters.has_attachments) count++;
    return count;
  };

  const handleSaveFilter = () => {
    if (onSaveFilter && filterName.trim()) {
      onSaveFilter(filterName.trim(), filters);
      setFilterName('');
      setSaveDialogOpen(false);
    }
  };

  const applyPresetFilter = (preset: any) => {
    onFiltersChange(preset.filters);
    setSearchTerm(preset.filters.search || '');
  };

  const activeFiltersCount = getActiveFiltersCount();

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ru}>
      <Paper sx={{ p: 3, mb: 3 }}>
        {/* Поиск и основные кнопки */}
        <Box display="flex" gap={2} alignItems="center" mb={2}>
          <TextField
            placeholder="Поиск по названию, описанию, номеру дефекта..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            fullWidth
            InputProps={{
              startAdornment: <SearchIcon sx={{ color: 'text.secondary', mr: 1 }} />
            }}
            size="medium"
          />
          
          <Badge badgeContent={activeFiltersCount} color="primary">
            <Button
              variant={expanded ? "contained" : "outlined"}
              startIcon={expanded ? <ExpandLessIcon /> : <FilterIcon />}
              onClick={() => setExpanded(!expanded)}
              sx={{ minWidth: 120 }}
            >
              Фильтры
            </Button>
          </Badge>

          {activeFiltersCount > 0 && (
            <Tooltip title="Очистить все фильтры">
              <IconButton onClick={clearAllFilters} color="error">
                <ClearIcon />
              </IconButton>
            </Tooltip>
          )}

          {onSaveFilter && (
            <Tooltip title="Сохранить фильтр">
              <IconButton onClick={() => setSaveDialogOpen(true)}>
                <BookmarkBorderIcon />
              </IconButton>
            </Tooltip>
          )}
        </Box>

        {/* Сохраненные фильтры */}
        {savedFilters.length > 0 && (
          <Box mb={2}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Сохраненные фильтры:
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {savedFilters.map((preset, index) => (
                <Chip
                  key={index}
                  label={preset.name}
                  icon={<BookmarkIcon />}
                  onClick={() => applyPresetFilter(preset)}
                  variant="outlined"
                  size="small"
                />
              ))}
            </Box>
          </Box>
        )}

        {/* Расширенные фильтры */}
        <Collapse in={expanded}>
          <Divider sx={{ mb: 3 }} />
          
          <Grid container spacing={3}>
            {/* Проекты */}
            <Grid item xs={12} sm={6} md={4}>
              <Autocomplete
                multiple
                options={projects}
                getOptionLabel={(project) => project.name}
                value={projects.filter(p => filters.project?.includes(p.id)) || []}
                onChange={(_, newValue) => 
                  handleFilterChange('project', newValue.map(p => p.id))
                }
                renderInput={(params) => (
                  <TextField {...params} label="Проекты" size="small" />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      variant="outlined"
                      label={option.name}
                      size="small"
                      {...getTagProps({ index })}
                    />
                  ))
                }
              />
            </Grid>

            {/* Статусы */}
            <Grid item xs={12} sm={6} md={4}>
              <Autocomplete
                multiple
                options={statusOptions}
                getOptionLabel={(option) => option.label}
                value={statusOptions.filter(s => filters.status?.includes(s.value)) || []}
                onChange={(_, newValue) => 
                  handleFilterChange('status', newValue.map(s => s.value))
                }
                renderInput={(params) => (
                  <TextField {...params} label="Статусы" size="small" />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      variant="outlined"
                      label={option.label}
                      size="small"
                      sx={{ 
                        color: option.color,
                        borderColor: option.color + '40'
                      }}
                      {...getTagProps({ index })}
                    />
                  ))
                }
              />
            </Grid>

            {/* Приоритеты */}
            <Grid item xs={12} sm={6} md={4}>
              <Autocomplete
                multiple
                options={priorityOptions}
                getOptionLabel={(option) => option.label}
                value={priorityOptions.filter(p => filters.priority?.includes(p.value)) || []}
                onChange={(_, newValue) => 
                  handleFilterChange('priority', newValue.map(p => p.value))
                }
                renderInput={(params) => (
                  <TextField {...params} label="Приоритеты" size="small" />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      variant="outlined"
                      label={option.label}
                      size="small"
                      sx={{ 
                        color: option.color,
                        borderColor: option.color + '40'
                      }}
                      {...getTagProps({ index })}
                    />
                  ))
                }
              />
            </Grid>

            {/* Серьезность */}
            <Grid item xs={12} sm={6} md={4}>
              <Autocomplete
                multiple
                options={severityOptions}
                getOptionLabel={(option) => option.label}
                value={severityOptions.filter(s => filters.severity?.includes(s.value)) || []}
                onChange={(_, newValue) => 
                  handleFilterChange('severity', newValue.map(s => s.value))
                }
                renderInput={(params) => (
                  <TextField {...params} label="Серьезность" size="small" />
                )}
              />
            </Grid>

            {/* Категории */}
            <Grid item xs={12} sm={6} md={4}>
              <Autocomplete
                multiple
                options={categories}
                value={filters.category || []}
                onChange={(_, newValue) => handleFilterChange('category', newValue)}
                renderInput={(params) => (
                  <TextField {...params} label="Категории" size="small" />
                )}
              />
            </Grid>

            {/* Исполнители */}
            <Grid item xs={12} sm={6} md={4}>
              <Autocomplete
                multiple
                options={users}
                getOptionLabel={(user) => `${user.first_name} ${user.last_name}`}
                value={users.filter(u => filters.assignee?.includes(u.id)) || []}
                onChange={(_, newValue) => 
                  handleFilterChange('assignee', newValue.map(u => u.id))
                }
                renderInput={(params) => (
                  <TextField {...params} label="Исполнители" size="small" />
                )}
              />
            </Grid>

            {/* Даты создания */}
            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="Создан с"
                value={filters.created_after}
                onChange={(date) => handleFilterChange('created_after', date)}
                slots={{ textField: TextField }}
                slotProps={{ 
                  textField: { 
                    size: 'small',
                    fullWidth: true
                  }
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="Создан до"
                value={filters.created_before}
                onChange={(date) => handleFilterChange('created_before', date)}
                slots={{ textField: TextField }}
                slotProps={{ 
                  textField: { 
                    size: 'small',
                    fullWidth: true
                  }
                }}
              />
            </Grid>

            {/* Сроки выполнения */}
            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="Срок с"
                value={filters.due_after}
                onChange={(date) => handleFilterChange('due_after', date)}
                slots={{ textField: TextField }}
                slotProps={{ 
                  textField: { 
                    size: 'small',
                    fullWidth: true
                  }
                }}
              />
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <DatePicker
                label="Срок до"
                value={filters.due_before}
                onChange={(date) => handleFilterChange('due_before', date)}
                slots={{ textField: TextField }}
                slotProps={{ 
                  textField: { 
                    size: 'small',
                    fullWidth: true
                  }
                }}
              />
            </Grid>

            {/* Дополнительные фильтры */}
            <Grid item xs={12}>
              <Box display="flex" gap={2} flexWrap="wrap">
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={filters.is_overdue || false}
                      onChange={(e) => handleFilterChange('is_overdue', e.target.checked)}
                    />
                  }
                  label="Только просроченные"
                />
                
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={filters.has_attachments || false}
                      onChange={(e) => handleFilterChange('has_attachments', e.target.checked)}
                    />
                  }
                  label="С вложениями"
                />
                
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={filters.assigned_to_me || false}
                      onChange={(e) => handleFilterChange('assigned_to_me', e.target.checked)}
                    />
                  }
                  label="Назначенные мне"
                />
                
                <FormControlLabel
                  control={
                    <Checkbox
                      checked={filters.created_by_me || false}
                      onChange={(e) => handleFilterChange('created_by_me', e.target.checked)}
                    />
                  }
                  label="Созданные мной"
                />
              </Box>
            </Grid>
          </Grid>

          {/* Сохранение фильтра */}
          {saveDialogOpen && (
            <Box mt={3} p={2} bgcolor="background.default" borderRadius={1}>
              <Typography variant="subtitle2" gutterBottom>
                Сохранить текущий фильтр
              </Typography>
              <Box display="flex" gap={2} alignItems="center">
                <TextField
                  label="Название фильтра"
                  value={filterName}
                  onChange={(e) => setFilterName(e.target.value)}
                  size="small"
                  sx={{ flexGrow: 1 }}
                />
                <Button
                  variant="contained"
                  startIcon={<SaveIcon />}
                  onClick={handleSaveFilter}
                  disabled={!filterName.trim()}
                >
                  Сохранить
                </Button>
                <Button onClick={() => setSaveDialogOpen(false)}>
                  Отмена
                </Button>
              </Box>
            </Box>
          )}
        </Collapse>

        {/* Активные фильтры */}
        {activeFiltersCount > 0 && (
          <Box mt={2}>
            <Typography variant="caption" color="text.secondary" gutterBottom>
              Активные фильтры ({activeFiltersCount}):
            </Typography>
            <Box display="flex" gap={1} flexWrap="wrap">
              {filters.search && (
                <Chip
                  label={`Поиск: "${filters.search}"`}
                  onDelete={() => {
                    setSearchTerm('');
                    handleFilterChange('search', '');
                  }}
                  size="small"
                />
              )}
              
              {filters.project?.length > 0 && (
                <Chip
                  label={`Проекты: ${filters.project.length}`}
                  onDelete={() => handleFilterChange('project', [])}
                  size="small"
                />
              )}
              
              {filters.status?.length > 0 && (
                <Chip
                  label={`Статусы: ${filters.status.length}`}
                  onDelete={() => handleFilterChange('status', [])}
                  size="small"
                />
              )}
              
              {filters.priority?.length > 0 && (
                <Chip
                  label={`Приоритеты: ${filters.priority.length}`}
                  onDelete={() => handleFilterChange('priority', [])}
                  size="small"
                />
              )}
              
              {filters.is_overdue && (
                <Chip
                  label="Просроченные"
                  onDelete={() => handleFilterChange('is_overdue', false)}
                  size="small"
                  color="error"
                />
              )}
              
              {filters.assigned_to_me && (
                <Chip
                  label="Мои задачи"
                  onDelete={() => handleFilterChange('assigned_to_me', false)}
                  size="small"
                  color="primary"
                />
              )}
            </Box>
          </Box>
        )}
      </Paper>
    </LocalizationProvider>
  );
};
