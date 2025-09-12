/**
 * Redux slice для управления отчетами
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { reportsAPI } from '../../services/api';

// Типы
export interface ReportTemplate {
  id: number;
  name: string;
  description: string;
  report_type: 'project_summary' | 'defects_analysis' | 'performance_report' | 'timeline_report' | 'custom';
  output_format: 'pdf' | 'excel' | 'csv' | 'json';
  is_public: boolean;
  is_active: boolean;
  created_by_name: string;
  reports_count: number;
  created_at: string;
}

export interface GeneratedReport {
  id: number;
  template_name: string;
  name: string;
  description: string;
  project_name?: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'expired';
  file_url?: string;
  formatted_file_size?: string;
  generated_by_name: string;
  generated_at?: string;
  download_count: number;
  is_expired: boolean;
  created_at: string;
}

export interface Dashboard {
  id: number;
  name: string;
  description: string;
  dashboard_type: 'executive' | 'project_manager' | 'engineer' | 'custom';
  widgets_config: any[];
  is_default: boolean;
  is_public: boolean;
  can_edit: boolean;
  created_at: string;
}

export interface Analytics {
  [key: string]: any;
}

export interface ReportsState {
  // Шаблоны отчетов
  templates: ReportTemplate[];
  currentTemplate: ReportTemplate | null;
  
  // Сгенерированные отчеты
  generatedReports: GeneratedReport[];
  currentReport: GeneratedReport | null;
  
  // Дашборды
  dashboards: Dashboard[];
  currentDashboard: Dashboard | null;
  
  // Аналитика
  analytics: {
    [key: string]: Analytics;
  };
  
  // Состояние загрузки
  isLoading: boolean;
  error: string | null;
  
  // Пагинация
  pagination: {
    page: number;
    pageSize: number;
    totalCount: number;
  };
}

// Начальное состояние
const initialState: ReportsState = {
  templates: [],
  currentTemplate: null,
  generatedReports: [],
  currentReport: null,
  dashboards: [],
  currentDashboard: null,
  analytics: {},
  isLoading: false,
  error: null,
  pagination: {
    page: 1,
    pageSize: 20,
    totalCount: 0,
  },
};

// Async thunks
export const fetchReportTemplates = createAsyncThunk(
  'reports/fetchTemplates',
  async (params: { page?: number; pageSize?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getTemplates(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки шаблонов');
    }
  }
);

export const fetchGeneratedReports = createAsyncThunk(
  'reports/fetchGenerated',
  async (params: { page?: number; pageSize?: number } = {}, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getGeneratedReports(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки отчетов');
    }
  }
);

export const generateReport = createAsyncThunk(
  'reports/generate',
  async (data: {
    template: number;
    name: string;
    description?: string;
    project?: number;
    date_from?: string;
    date_to?: string;
    filter_params?: any;
  }, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.generateReport(data);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка генерации отчета');
    }
  }
);

export const fetchDashboards = createAsyncThunk(
  'reports/fetchDashboards',
  async (_, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getDashboards();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки дашбордов');
    }
  }
);

export const fetchProjectAnalytics = createAsyncThunk(
  'reports/fetchProjectAnalytics',
  async (params: {
    projectId: number;
    date_from?: string;
    date_to?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getProjectAnalytics(params.projectId, {
        date_from: params.date_from,
        date_to: params.date_to,
      });
      return { projectId: params.projectId, data: response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки аналитики');
    }
  }
);

export const fetchSystemAnalytics = createAsyncThunk(
  'reports/fetchSystemAnalytics',
  async (_, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getSystemAnalytics();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки системной аналитики');
    }
  }
);

export const fetchChartData = createAsyncThunk(
  'reports/fetchChartData',
  async (params: {
    type: string;
    project_id?: number;
  }, { rejectWithValue }) => {
    try {
      const response = await reportsAPI.getChartData(params);
      return { type: params.type, data: response };
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки данных графика');
    }
  }
);

// Slice
const reportsSlice = createSlice({
  name: 'reports',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setCurrentTemplate: (state, action: PayloadAction<ReportTemplate | null>) => {
      state.currentTemplate = action.payload;
    },
    setCurrentReport: (state, action: PayloadAction<GeneratedReport | null>) => {
      state.currentReport = action.payload;
    },
    setCurrentDashboard: (state, action: PayloadAction<Dashboard | null>) => {
      state.currentDashboard = action.payload;
    },
    clearAnalytics: (state, action: PayloadAction<string>) => {
      delete state.analytics[action.payload];
    },
    setPagination: (state, action: PayloadAction<Partial<ReportsState['pagination']>>) => {
      state.pagination = { ...state.pagination, ...action.payload };
    },
  },
  extraReducers: (builder) => {
    // Fetch templates
    builder
      .addCase(fetchReportTemplates.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchReportTemplates.fulfilled, (state, action) => {
        state.isLoading = false;
        state.templates = action.payload.results;
        state.pagination.totalCount = action.payload.count;
        state.error = null;
      })
      .addCase(fetchReportTemplates.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch generated reports
    builder
      .addCase(fetchGeneratedReports.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchGeneratedReports.fulfilled, (state, action) => {
        state.isLoading = false;
        state.generatedReports = action.payload.results;
        state.pagination.totalCount = action.payload.count;
        state.error = null;
      })
      .addCase(fetchGeneratedReports.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Generate report
    builder
      .addCase(generateReport.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(generateReport.fulfilled, (state, action) => {
        state.isLoading = false;
        state.generatedReports.unshift(action.payload);
        state.error = null;
      })
      .addCase(generateReport.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch dashboards
    builder
      .addCase(fetchDashboards.fulfilled, (state, action) => {
        state.dashboards = action.payload.results;
      });

    // Fetch project analytics
    builder
      .addCase(fetchProjectAnalytics.fulfilled, (state, action) => {
        state.analytics[`project_${action.payload.projectId}`] = action.payload.data;
      });

    // Fetch system analytics
    builder
      .addCase(fetchSystemAnalytics.fulfilled, (state, action) => {
        state.analytics['system'] = action.payload;
      });

    // Fetch chart data
    builder
      .addCase(fetchChartData.fulfilled, (state, action) => {
        state.analytics[`chart_${action.payload.type}`] = action.payload.data;
      });
  },
});

// Actions
export const {
  clearError,
  setCurrentTemplate,
  setCurrentReport,
  setCurrentDashboard,
  clearAnalytics,
  setPagination,
} = reportsSlice.actions;

// Selectors
export const selectReports = (state: { reports: ReportsState }) => state.reports;
export const selectTemplates = (state: { reports: ReportsState }) => state.reports.templates;
export const selectGeneratedReports = (state: { reports: ReportsState }) => state.reports.generatedReports;
export const selectDashboards = (state: { reports: ReportsState }) => state.reports.dashboards;
export const selectReportsLoading = (state: { reports: ReportsState }) => state.reports.isLoading;
export const selectReportsError = (state: { reports: ReportsState }) => state.reports.error;
export const selectAnalytics = (state: { reports: ReportsState }, key: string) => 
  state.reports.analytics[key];

export default reportsSlice.reducer;
