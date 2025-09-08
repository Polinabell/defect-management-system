/**
 * Redux slice для управления состоянием UI
 */

import { createSlice, PayloadAction } from '@reduxjs/toolkit';

// Типы
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  persistent?: boolean;
}

export interface LoadingState {
  global: boolean;
  [key: string]: boolean;
}

export interface UIState {
  // Навигация
  sidebarOpen: boolean;
  sidebarMobile: boolean;
  
  // Загрузка
  loading: LoadingState;
  
  // Уведомления
  notifications: Notification[];
  
  // Модальные окна
  modals: {
    [key: string]: boolean;
  };
  
  // Настройки интерфейса
  theme: 'light' | 'dark';
  language: 'ru' | 'en';
  
  // Фильтры и сортировка
  filters: {
    [key: string]: any;
  };
  
  // Состояние таблиц
  tables: {
    [key: string]: {
      page: number;
      rowsPerPage: number;
      orderBy: string;
      order: 'asc' | 'desc';
      selected: any[];
    };
  };
  
  // Настройки отображения
  viewSettings: {
    [key: string]: {
      view: 'list' | 'grid' | 'kanban';
      density: 'comfortable' | 'standard' | 'compact';
      columns: string[];
    };
  };
}

// Начальное состояние
const initialState: UIState = {
  sidebarOpen: true,
  sidebarMobile: false,
  loading: {
    global: false,
  },
  notifications: [],
  modals: {},
  theme: 'light',
  language: 'ru',
  filters: {},
  tables: {},
  viewSettings: {},
};

// Slice
const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    // Навигация
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action: PayloadAction<boolean>) => {
      state.sidebarOpen = action.payload;
    },
    setSidebarMobile: (state, action: PayloadAction<boolean>) => {
      state.sidebarMobile = action.payload;
    },
    
    // Загрузка
    setLoading: (state, action: PayloadAction<{ key?: string; loading: boolean }>) => {
      const { key = 'global', loading } = action.payload;
      state.loading[key] = loading;
    },
    
    // Уведомления
    addNotification: (state, action: PayloadAction<Omit<Notification, 'id'>>) => {
      const notification: Notification = {
        ...action.payload,
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      };
      state.notifications.push(notification);
    },
    removeNotification: (state, action: PayloadAction<string>) => {
      state.notifications = state.notifications.filter(
        (notification) => notification.id !== action.payload
      );
    },
    clearNotifications: (state) => {
      state.notifications = [];
    },
    
    // Модальные окна
    openModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = true;
    },
    closeModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = false;
    },
    toggleModal: (state, action: PayloadAction<string>) => {
      state.modals[action.payload] = !state.modals[action.payload];
    },
    
    // Настройки интерфейса
    setTheme: (state, action: PayloadAction<'light' | 'dark'>) => {
      state.theme = action.payload;
    },
    setLanguage: (state, action: PayloadAction<'ru' | 'en'>) => {
      state.language = action.payload;
    },
    
    // Фильтры
    setFilter: (state, action: PayloadAction<{ key: string; value: any }>) => {
      state.filters[action.payload.key] = action.payload.value;
    },
    clearFilter: (state, action: PayloadAction<string>) => {
      delete state.filters[action.payload];
    },
    clearAllFilters: (state) => {
      state.filters = {};
    },
    
    // Таблицы
    setTableState: (state, action: PayloadAction<{
      tableKey: string;
      page?: number;
      rowsPerPage?: number;
      orderBy?: string;
      order?: 'asc' | 'desc';
      selected?: any[];
    }>) => {
      const { tableKey, ...tableState } = action.payload;
      
      if (!state.tables[tableKey]) {
        state.tables[tableKey] = {
          page: 0,
          rowsPerPage: 25,
          orderBy: '',
          order: 'asc',
          selected: [],
        };
      }
      
      state.tables[tableKey] = {
        ...state.tables[tableKey],
        ...tableState,
      };
    },
    clearTableSelection: (state, action: PayloadAction<string>) => {
      if (state.tables[action.payload]) {
        state.tables[action.payload].selected = [];
      }
    },
    
    // Настройки отображения
    setViewSettings: (state, action: PayloadAction<{
      key: string;
      view?: 'list' | 'grid' | 'kanban';
      density?: 'comfortable' | 'standard' | 'compact';
      columns?: string[];
    }>) => {
      const { key, ...settings } = action.payload;
      
      if (!state.viewSettings[key]) {
        state.viewSettings[key] = {
          view: 'list',
          density: 'standard',
          columns: [],
        };
      }
      
      state.viewSettings[key] = {
        ...state.viewSettings[key],
        ...settings,
      };
    },
  },
});

// Actions
export const {
  toggleSidebar,
  setSidebarOpen,
  setSidebarMobile,
  setLoading,
  addNotification,
  removeNotification,
  clearNotifications,
  openModal,
  closeModal,
  toggleModal,
  setTheme,
  setLanguage,
  setFilter,
  clearFilter,
  clearAllFilters,
  setTableState,
  clearTableSelection,
  setViewSettings,
} = uiSlice.actions;

// Selectors
export const selectUI = (state: { ui: UIState }) => state.ui;
export const selectSidebarOpen = (state: { ui: UIState }) => state.ui.sidebarOpen;
export const selectLoading = (state: { ui: UIState }, key: string = 'global') => 
  state.ui.loading[key] || false;
export const selectNotifications = (state: { ui: UIState }) => state.ui.notifications;
export const selectModal = (state: { ui: UIState }, key: string) => 
  state.ui.modals[key] || false;
export const selectTheme = (state: { ui: UIState }) => state.ui.theme;
export const selectLanguage = (state: { ui: UIState }) => state.ui.language;
export const selectFilter = (state: { ui: UIState }, key: string) => 
  state.ui.filters[key];
export const selectTableState = (state: { ui: UIState }, tableKey: string) => 
  state.ui.tables[tableKey] || {
    page: 0,
    rowsPerPage: 25,
    orderBy: '',
    order: 'asc' as const,
    selected: [],
  };
export const selectViewSettings = (state: { ui: UIState }, key: string) => 
  state.ui.viewSettings[key] || {
    view: 'list' as const,
    density: 'standard' as const,
    columns: [],
  };

export default uiSlice.reducer;
