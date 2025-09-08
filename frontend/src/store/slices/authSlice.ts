/**
 * Redux slice для управления аутентификацией
 */

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authAPI } from '../../services/api';

// Типы
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'engineer' | 'manager' | 'observer';
  is_active: boolean;
  phone?: string;
  avatar?: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  lastActivity: number | null;
}

// Начальное состояние
const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('accessToken'),
  refreshToken: localStorage.getItem('refreshToken'),
  isAuthenticated: !!localStorage.getItem('accessToken'),
  isLoading: false,
  error: null,
  lastActivity: null,
};

// Async thunks
export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: { username: string; password: string }, { rejectWithValue }) => {
    try {
      const response = await authAPI.login(credentials);
      
      // Сохраняем токены в localStorage
      localStorage.setItem('accessToken', response.access);
      localStorage.setItem('refreshToken', response.refresh);
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка входа');
    }
  }
);

export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData: {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    password: string;
    role?: string;
  }, { rejectWithValue }) => {
    try {
      const response = await authAPI.register(userData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка регистрации');
    }
  }
);

export const getCurrentUser = createAsyncThunk(
  'auth/getCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authAPI.getCurrentUser();
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Ошибка получения пользователя');
    }
  }
);

export const updateProfile = createAsyncThunk(
  'auth/updateProfile',
  async (userData: Partial<User>, { rejectWithValue }) => {
    try {
      const response = await authAPI.updateProfile(userData);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка обновления профиля');
    }
  }
);

export const changePassword = createAsyncThunk(
  'auth/changePassword',
  async (passwords: {
    old_password: string;
    new_password: string;
  }, { rejectWithValue }) => {
    try {
      await authAPI.changePassword(passwords);
      return 'Пароль успешно изменён';
    } catch (error: any) {
      return rejectWithValue(error.response?.data || 'Ошибка изменения пароля');
    }
  }
);

export const refreshAccessToken = createAsyncThunk(
  'auth/refreshToken',
  async (_, { getState, rejectWithValue }) => {
    try {
      const state = getState() as { auth: AuthState };
      const refreshToken = state.auth.refreshToken;
      
      if (!refreshToken) {
        throw new Error('Нет refresh токена');
      }
      
      const response = await authAPI.refreshToken(refreshToken);
      
      // Обновляем токен в localStorage
      localStorage.setItem('accessToken', response.access);
      
      return response;
    } catch (error: any) {
      // Очищаем токены при ошибке обновления
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      return rejectWithValue(error.response?.data?.detail || 'Ошибка обновления токена');
    }
  }
);

// Slice
const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.refreshToken = null;
      state.isAuthenticated = false;
      state.error = null;
      state.lastActivity = null;
      
      // Очищаем localStorage
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    },
    clearError: (state) => {
      state.error = null;
    },
    updateLastActivity: (state) => {
      state.lastActivity = Date.now();
    },
    setToken: (state, action: PayloadAction<string>) => {
      state.token = action.payload;
      state.isAuthenticated = true;
      localStorage.setItem('accessToken', action.payload);
    },
  },
  extraReducers: (builder) => {
    // Login
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.token = action.payload.access;
        state.refreshToken = action.payload.refresh;
        state.user = action.payload.user;
        state.isAuthenticated = true;
        state.lastActivity = Date.now();
        state.error = null;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Register
    builder
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state) => {
        state.isLoading = false;
        state.error = null;
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Get current user
    builder
      .addCase(getCurrentUser.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(getCurrentUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(getCurrentUser.rejected, (state, action) => {
        state.isLoading = false;
        state.user = null;
        state.isAuthenticated = false;
        state.error = action.payload as string;
        
        // Очищаем токены при ошибке
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
      });

    // Update profile
    builder
      .addCase(updateProfile.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateProfile.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = { ...state.user, ...action.payload };
        state.error = null;
      })
      .addCase(updateProfile.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Change password
    builder
      .addCase(changePassword.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(changePassword.fulfilled, (state) => {
        state.isLoading = false;
        state.error = null;
      })
      .addCase(changePassword.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });

    // Refresh token
    builder
      .addCase(refreshAccessToken.fulfilled, (state, action) => {
        state.token = action.payload.access;
        state.isAuthenticated = true;
        state.lastActivity = Date.now();
      })
      .addCase(refreshAccessToken.rejected, (state) => {
        state.user = null;
        state.token = null;
        state.refreshToken = null;
        state.isAuthenticated = false;
        state.lastActivity = null;
      });
  },
});

// Actions
export const { logout, clearError, updateLastActivity, setToken } = authSlice.actions;

// Selectors
export const selectAuth = (state: { auth: AuthState }) => state.auth;
export const selectUser = (state: { auth: AuthState }) => state.auth.user;
export const selectIsAuthenticated = (state: { auth: AuthState }) => state.auth.isAuthenticated;
export const selectAuthLoading = (state: { auth: AuthState }) => state.auth.isLoading;
export const selectAuthError = (state: { auth: AuthState }) => state.auth.error;

export default authSlice.reducer;
