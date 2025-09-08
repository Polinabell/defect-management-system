/**
 * Redux slice для управления дефектами
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { defectsAPI } from '../../services/api';

// Типы
export interface Defect {
  id: number;
  defect_number: string;
  title: string;
  description: string;
  status: 'new' | 'in_progress' | 'review' | 'closed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  severity: 'cosmetic' | 'minor' | 'major' | 'critical' | 'blocking';
  project: {
    id: number;
    name: string;
  };
  category: {
    id: number;
    name: string;
    color: string;
  };
  author: {
    id: number;
    first_name: string;
    last_name: string;
  };
  assignee?: {
    id: number;
    first_name: string;
    last_name: string;
  };
  location: string;
  floor?: string;
  room?: string;
  due_date?: string;
  is_overdue: boolean;
  days_remaining?: number;
  main_image?: {
    id: number;
    file_url: string;
    filename: string;
  };
  comments_count: number;
  created_at: string;
  updated_at: string;
}

export interface DefectsState {
  defects: Defect[];
  currentDefect: Defect | null;
  totalCount: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  error: string | null;
  filters: {
    search?: string;
    status?: string[];
    priority?: string[];
    severity?: string[];
    project?: number;
    category?: number;
    assignee?: number;
    author?: number;
    is_overdue?: boolean;
  };
}

// Начальное состояние
const initialState: DefectsState = {
  defects: [],
  currentDefect: null,
  totalCount: 0,
  page: 1,
  pageSize: 20,
  isLoading: false,
  error: null,
  filters: {},
};

// Async thunks
export const fetchDefects = createAsyncThunk(
  'defects/fetchDefects',
  async (params: {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: string[];
    priority?: string[];
    project?: number;
  } = {}, { rejectWithValue }) => {
    try {
      const response = await defectsAPI.getDefects(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки дефектов');
    }
  }
);

export const fetchDefect = createAsyncThunk(
  'defects/fetchDefect',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await defectsAPI.getDefect(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки дефекта');
    }
  }
);

export const createDefect = createAsyncThunk(
  'defects/createDefect',
  async (defectData: FormData, { rejectWithValue }) => {
    try {
      const response = await defectsAPI.createDefect(defectData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка создания дефекта');
    }
  }
);

export const updateDefect = createAsyncThunk(
  'defects/updateDefect',
  async ({ id, data }: { id: number; data: Partial<Defect> }, { rejectWithValue }) => {
    try {
      const response = await defectsAPI.updateDefect(id, data);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка обновления дефекта');
    }
  }
);

export const changeDefectStatus = createAsyncThunk(
  'defects/changeStatus',
  async ({ id, status, comment }: { id: number; status: string; comment?: string }, { rejectWithValue }) => {
    try {
      const response = await defectsAPI.changeStatus(id, status, comment);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка изменения статуса');
    }
  }
);

export const assignDefect = createAsyncThunk(
  'defects/assign',
  async ({ id, assignee, due_date, comment }: {
    id: number;
    assignee: number;
    due_date?: string;
    comment?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await defectsAPI.assign(id, assignee, due_date, comment);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка назначения исполнителя');
    }
  }
);

// Slice
const defectsSlice = createSlice({
  name: 'defects',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<DefectsState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearFilters: (state) => {
      state.filters = {};
    },
    setPage: (state, action: PayloadAction<number>) => {
      state.page = action.payload;
    },
    setPageSize: (state, action: PayloadAction<number>) => {
      state.pageSize = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    setCurrentDefect: (state, action: PayloadAction<Defect | null>) => {
      state.currentDefect = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch defects
    builder
      .addCase(fetchDefects.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchDefects.fulfilled, (state, action) => {
        state.isLoading = false;
        state.defects = action.payload.results;
        state.totalCount = action.payload.count;
        state.error = null;
      })
      .addCase(fetchDefects.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch defect
    builder
      .addCase(fetchDefect.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchDefect.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentDefect = action.payload;
        state.error = null;
      })
      .addCase(fetchDefect.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create defect
    builder
      .addCase(createDefect.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createDefect.fulfilled, (state, action) => {
        state.isLoading = false;
        state.defects.unshift(action.payload);
        state.totalCount += 1;
        state.error = null;
      })
      .addCase(createDefect.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update defect
    builder
      .addCase(updateDefect.fulfilled, (state, action) => {
        const index = state.defects.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.defects[index] = action.payload;
        }
        if (state.currentDefect?.id === action.payload.id) {
          state.currentDefect = action.payload;
        }
      });

    // Change status
    builder
      .addCase(changeDefectStatus.fulfilled, (state, action) => {
        const index = state.defects.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.defects[index] = action.payload;
        }
        if (state.currentDefect?.id === action.payload.id) {
          state.currentDefect = action.payload;
        }
      });

    // Assign defect
    builder
      .addCase(assignDefect.fulfilled, (state, action) => {
        const index = state.defects.findIndex(d => d.id === action.payload.id);
        if (index !== -1) {
          state.defects[index] = action.payload;
        }
        if (state.currentDefect?.id === action.payload.id) {
          state.currentDefect = action.payload;
        }
      });
  },
});

// Actions
export const {
  setFilters,
  clearFilters,
  setPage,
  setPageSize,
  clearError,
  setCurrentDefect,
} = defectsSlice.actions;

// Selectors
export const selectDefects = (state: { defects: DefectsState }) => state.defects;
export const selectDefectsList = (state: { defects: DefectsState }) => state.defects.defects;
export const selectCurrentDefect = (state: { defects: DefectsState }) => state.defects.currentDefect;
export const selectDefectsLoading = (state: { defects: DefectsState }) => state.defects.isLoading;
export const selectDefectsError = (state: { defects: DefectsState }) => state.defects.error;
export const selectDefectsFilters = (state: { defects: DefectsState }) => state.defects.filters;

export default defectsSlice.reducer;
