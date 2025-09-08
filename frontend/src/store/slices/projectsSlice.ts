/**
 * Redux slice для управления проектами
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { projectsAPI } from '../../services/api';

// Типы
export interface Project {
  id: number;
  name: string;
  description: string;
  status: 'planning' | 'in_progress' | 'on_hold' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  manager: {
    id: number;
    first_name: string;
    last_name: string;
  };
  start_date: string;
  end_date?: string;
  progress_percentage: number;
  defects_count: number;
  members_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectsState {
  projects: Project[];
  currentProject: Project | null;
  totalCount: number;
  page: number;
  pageSize: number;
  isLoading: boolean;
  error: string | null;
  filters: {
    search?: string;
    status?: string[];
    priority?: string[];
    manager?: number;
  };
}

// Начальное состояние
const initialState: ProjectsState = {
  projects: [],
  currentProject: null,
  totalCount: 0,
  page: 1,
  pageSize: 20,
  isLoading: false,
  error: null,
  filters: {},
};

// Async thunks
export const fetchProjects = createAsyncThunk(
  'projects/fetchProjects',
  async (params: {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: string[];
    priority?: string[];
  } = {}, { rejectWithValue }) => {
    try {
      const response = await projectsAPI.getProjects(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки проектов');
    }
  }
);

export const fetchProject = createAsyncThunk(
  'projects/fetchProject',
  async (id: number, { rejectWithValue }) => {
    try {
      const response = await projectsAPI.getProject(id);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка загрузки проекта');
    }
  }
);

export const createProject = createAsyncThunk(
  'projects/createProject',
  async (projectData: Partial<Project>, { rejectWithValue }) => {
    try {
      const response = await projectsAPI.createProject(projectData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка создания проекта');
    }
  }
);

export const updateProject = createAsyncThunk(
  'projects/updateProject',
  async ({ id, data }: { id: number; data: Partial<Project> }, { rejectWithValue }) => {
    try {
      const response = await projectsAPI.updateProject(id, data);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка обновления проекта');
    }
  }
);

export const deleteProject = createAsyncThunk(
  'projects/deleteProject',
  async (id: number, { rejectWithValue }) => {
    try {
      await projectsAPI.deleteProject(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка удаления проекта');
    }
  }
);

// Slice
const projectsSlice = createSlice({
  name: 'projects',
  initialState,
  reducers: {
    setFilters: (state, action: PayloadAction<Partial<ProjectsState['filters']>>) => {
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
    setCurrentProject: (state, action: PayloadAction<Project | null>) => {
      state.currentProject = action.payload;
    },
  },
  extraReducers: (builder) => {
    // Fetch projects
    builder
      .addCase(fetchProjects.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchProjects.fulfilled, (state, action) => {
        state.isLoading = false;
        state.projects = action.payload.results;
        state.totalCount = action.payload.count;
        state.error = null;
      })
      .addCase(fetchProjects.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Fetch project
    builder
      .addCase(fetchProject.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchProject.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentProject = action.payload;
        state.error = null;
      })
      .addCase(fetchProject.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Create project
    builder
      .addCase(createProject.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createProject.fulfilled, (state, action) => {
        state.isLoading = false;
        state.projects.unshift(action.payload);
        state.totalCount += 1;
        state.error = null;
      })
      .addCase(createProject.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Update project
    builder
      .addCase(updateProject.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateProject.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.projects.findIndex(p => p.id === action.payload.id);
        if (index !== -1) {
          state.projects[index] = action.payload;
        }
        if (state.currentProject?.id === action.payload.id) {
          state.currentProject = action.payload;
        }
        state.error = null;
      })
      .addCase(updateProject.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Delete project
    builder
      .addCase(deleteProject.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteProject.fulfilled, (state, action) => {
        state.isLoading = false;
        state.projects = state.projects.filter(p => p.id !== action.payload);
        state.totalCount -= 1;
        if (state.currentProject?.id === action.payload) {
          state.currentProject = null;
        }
        state.error = null;
      })
      .addCase(deleteProject.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
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
  setCurrentProject,
} = projectsSlice.actions;

// Selectors
export const selectProjects = (state: { projects: ProjectsState }) => state.projects;
export const selectProjectsList = (state: { projects: ProjectsState }) => state.projects.projects;
export const selectCurrentProject = (state: { projects: ProjectsState }) => state.projects.currentProject;
export const selectProjectsLoading = (state: { projects: ProjectsState }) => state.projects.isLoading;
export const selectProjectsError = (state: { projects: ProjectsState }) => state.projects.error;
export const selectProjectsFilters = (state: { projects: ProjectsState }) => state.projects.filters;
export const selectProjectsPagination = (state: { projects: ProjectsState }) => ({
  page: state.projects.page,
  pageSize: state.projects.pageSize,
  totalCount: state.projects.totalCount,
});

export default projectsSlice.reducer;
