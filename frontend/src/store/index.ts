/**
 * Настройка Redux Store с Redux Toolkit
 */

import { configureStore } from '@reduxjs/toolkit';
import { useDispatch, useSelector, TypedUseSelectorHook } from 'react-redux';

// Импорт reducers
import authReducer from './slices/authSlice';
import uiReducer from './slices/uiSlice';
import projectsReducer from './slices/projectsSlice';
import defectsReducer from './slices/defectsSlice';
import reportsReducer from './slices/reportsSlice';

// Настройка store
export const store = configureStore({
  reducer: {
    auth: authReducer,
    ui: uiReducer,
    projects: projectsReducer,
    defects: defectsReducer,
    reports: reportsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: ['persist/PERSIST'],
      },
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Типы для TypeScript
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

// Типизированные хуки
export const useAppDispatch = () => useDispatch<AppDispatch>();
export const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;

export default store;
