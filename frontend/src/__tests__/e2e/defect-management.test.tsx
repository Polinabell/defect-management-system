/**
 * End-to-End тесты для управления дефектами
 */

import React from 'react';
import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { configureStore } from '@reduxjs/toolkit';

import App from '../../App';
import { theme } from '../../theme';
import authReducer from '../../store/slices/authSlice';
import projectsReducer from '../../store/slices/projectsSlice';
import defectsReducer from '../../store/slices/defectsSlice';
import { Defects } from '../../pages/Defects';
import { DefectDetail } from '../../pages/DefectDetail';
import { Login } from '../../pages/auth/Login';
import { AuthProvider } from '../../contexts/AuthContext';

// Мокируем API для e2e тестов
jest.mock('../../services/api', () => ({
  authAPI: {
    login: jest.fn((credentials) => {
      if (credentials.username === 'manager' && credentials.password === 'password') {
        return Promise.resolve({
          token: 'mock-token',
          user: {
            id: 1,
            username: 'manager',
            role: 'manager',
            first_name: 'Анна',
            last_name: 'Менеджерова'
          }
        });
      }
      return Promise.reject(new Error('Invalid credentials'));
    }),
    logout: jest.fn(() => Promise.resolve({ success: true })),
    getCurrentUser: jest.fn(() => Promise.resolve(null))
  },
  defectsAPI: {
    getDefects: jest.fn(() => Promise.resolve({
      results: [
        {
          id: 1,
          defect_number: 'DEF-2024-001',
          title: 'Трещина в стене',
          description: 'Обнаружена трещина в несущей стене',
          status: 'new',
          priority: 'high',
          severity: 'major',
          project: { id: 1, name: 'Жилой комплекс "Север"' },
          category: { id: 1, name: 'Структурные дефекты', color: '#f44336' },
          author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
          reporter: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
          location: 'Здание A, секция 1',
          floor: '5',
          room: 'Квартира 501',
          comments_count: 3,
          created_at: '2024-09-01T10:00:00Z',
          updated_at: '2024-09-08T15:30:00Z'
        },
        {
          id: 2,
          defect_number: 'DEF-2024-002',
          title: 'Неработающая розетка',
          description: 'Розетка в кухне не подает напряжение',
          status: 'in_progress',
          priority: 'medium',
          severity: 'minor',
          project: { id: 1, name: 'Жилой комплекс "Север"' },
          category: { id: 2, name: 'Электрические проблемы', color: '#ff9800' },
          author: { id: 2, first_name: 'Петр', last_name: 'Инженеров' },
          assignee: { id: 3, first_name: 'Мария', last_name: 'Электрикова' },
          reporter: { id: 2, first_name: 'Петр', last_name: 'Инженеров' },
          location: 'Здание A, секция 2',
          floor: '3',
          room: 'Квартира 302',
          due_date: '2024-09-15',
          comments_count: 1,
          created_at: '2024-08-28T14:20:00Z',
          updated_at: '2024-09-05T11:45:00Z'
        }
      ],
      count: 2
    })),
    getDefect: jest.fn((id) => {
      const defects = [
        {
          id: 1,
          defect_number: 'DEF-2024-001',
          title: 'Трещина в стене',
          description: 'Обнаружена трещина в несущей стене',
          status: 'new',
          priority: 'high',
          severity: 'major',
          project: { id: 1, name: 'Жилой комплекс "Север"' },
          category: { id: 1, name: 'Структурные дефекты', color: '#f44336' },
          author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
          reporter: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
          location: 'Здание A, секция 1',
          floor: '5',
          room: 'Квартира 501',
          comments_count: 3,
          created_at: '2024-09-01T10:00:00Z',
          updated_at: '2024-09-08T15:30:00Z'
        }
      ];
      const defect = defects.find(d => d.id === id);
      return defect ? Promise.resolve(defect) : Promise.reject(new Error('Дефект не найден'));
    }),
    createDefect: jest.fn((data) => Promise.resolve({
      id: 3,
      defect_number: 'DEF-2024-003',
      title: data.get('title'),
      description: data.get('description'),
      status: 'new',
      priority: data.get('priority') || 'medium',
      severity: data.get('severity') || 'minor',
      project: { id: 1, name: 'Жилой комплекс "Север"' },
      category: { id: 1, name: 'Структурные дефекты', color: '#f44336' },
      author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
      location: data.get('location') || '',
      comments_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    })),
    changeStatus: jest.fn((id, status) => Promise.resolve({
      id,
      status,
      updated_at: new Date().toISOString()
    })),
    getCategories: jest.fn(() => Promise.resolve([
      { id: 1, name: 'Структурные дефекты', color: '#f44336' },
      { id: 2, name: 'Электрические проблемы', color: '#ff9800' }
    ])),
    getEngineers: jest.fn(() => Promise.resolve([
      { id: 2, first_name: 'Петр', last_name: 'Инженеров', specialization: 'Конструкции' },
      { id: 3, first_name: 'Мария', last_name: 'Электрикова', specialization: 'Электрика' }
    ]))
  },
  projectsAPI: {
    getProjects: jest.fn(() => Promise.resolve({
      results: [
        { id: 1, name: 'Жилой комплекс "Север"' }
      ],
      count: 1
    }))
  },
  commentsAPI: {
    getDefectComments: jest.fn(() => Promise.resolve([
      {
        id: 1,
        defect_id: 1,
        author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова', role: 'manager' },
        content: 'Срочно необходимо устранить данный дефект',
        created_at: '2024-09-01T10:30:00Z',
        updated_at: '2024-09-01T10:30:00Z',
        is_internal: false,
        attachments: []
      }
    ])),
    addComment: jest.fn((defectId, content, isInternal) => Promise.resolve({
      id: 2,
      defect_id: defectId,
      author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова', role: 'manager' },
      content,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_internal: isInternal,
      attachments: []
    }))
  }
}));

const createMockStore = (preloadedState = {}) => configureStore({
  reducer: {
    auth: authReducer,
    projects: projectsReducer,
    defects: defectsReducer,
  },
  preloadedState: {
    auth: {
      user: null,
      token: null,
      isAuthenticated: false,
      permissions: []
    },
    projects: {
      projects: [],
      totalCount: 0,
      page: 1,
      pageSize: 20,
      isLoading: false,
      error: null,
      filters: {}
    },
    defects: {
      defects: [],
      totalCount: 0,
      page: 1,
      pageSize: 20,
      isLoading: false,
      error: null,
      filters: {}
    },
    ...preloadedState
  }
});

const renderApp = (initialRoute = '/') => {
  const store = createMockStore();
  
  window.history.pushState({}, 'Test page', initialRoute);
  
  return render(
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          <AuthProvider>
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/defects" element={<Defects />} />
              <Route path="/defects/:id" element={<DefectDetail />} />
              <Route path="*" element={<div>Not Found</div>} />
            </Routes>
          </AuthProvider>
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
};

describe('E2E: Управление дефектами', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  test('Полный цикл: вход, просмотр дефектов, создание дефекта', async () => {
    const user = userEvent.setup();
    
    // 1. Начинаем с экрана входа
    renderApp('/login');
    
    expect(screen.getByText('Вход в систему')).toBeInTheDocument();
    
    // 2. Заполняем форму входа
    await user.type(screen.getByLabelText(/имя пользователя/i), 'manager');
    await user.type(screen.getByLabelText(/пароль/i), 'password');
    await user.click(screen.getByRole('button', { name: /войти/i }));
    
    // 3. Переходим к странице дефектов
    renderApp('/defects');
    
    await waitFor(() => {
      expect(screen.getByText('Дефекты')).toBeInTheDocument();
    });
    
    // 4. Проверяем, что дефекты загружены
    await waitFor(() => {
      expect(screen.getByText('Трещина в стене')).toBeInTheDocument();
      expect(screen.getByText('Неработающая розетка')).toBeInTheDocument();
    });
    
    // 5. Открываем диалог создания дефекта
    const createButton = screen.getByRole('button', { name: /создать дефект/i });
    await user.click(createButton);
    
    await waitFor(() => {
      expect(screen.getByText('Создать дефект')).toBeInTheDocument();
    });
    
    // 6. Заполняем форму создания дефекта
    await user.type(screen.getByLabelText(/название/i), 'Новый тестовый дефект');
    await user.type(screen.getByLabelText(/описание/i), 'Описание нового дефекта');
    await user.type(screen.getByLabelText(/локация/i), 'Тестовая локация');
    
    // 7. Отправляем форму
    const submitButton = screen.getByRole('button', { name: /создать/i });
    await user.click(submitButton);
    
    // 8. Проверяем, что дефект создан
    await waitFor(() => {
      expect(screen.queryByText('Создать дефект')).not.toBeInTheDocument();
    });
  });

  test('Просмотр деталей дефекта и добавление комментария', async () => {
    const user = userEvent.setup();
    
    // Устанавливаем пользователя как авторизованного
    localStorage.setItem('token', 'mock-token');
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      username: 'manager',
      role: 'manager'
    }));
    
    // 1. Переходим к деталям дефекта
    renderApp('/defects/1');
    
    await waitFor(() => {
      expect(screen.getByText('Трещина в стене')).toBeInTheDocument();
      expect(screen.getByText('DEF-2024-001')).toBeInTheDocument();
    });
    
    // 2. Проверяем отображение информации о дефекте
    expect(screen.getByText('Обнаружена трещина в несущей стене')).toBeInTheDocument();
    expect(screen.getByText('Автор: Анна Менеджерова')).toBeInTheDocument();
    expect(screen.getByText('Локация: Здание A, секция 1, этаж 5, Квартира 501')).toBeInTheDocument();
    
    // 3. Переключаемся на таб комментариев
    const commentsTab = screen.getByText(/комментарии/i);
    await user.click(commentsTab);
    
    await waitFor(() => {
      expect(screen.getByText('Срочно необходимо устранить данный дефект')).toBeInTheDocument();
    });
    
    // 4. Добавляем новый комментарий
    const commentInput = screen.getByPlaceholderText(/введите комментарий/i);
    await user.type(commentInput, 'Новый тестовый комментарий');
    
    const sendButton = screen.getByRole('button', { name: /отправить/i });
    await user.click(sendButton);
    
    // 5. Проверяем, что комментарий добавлен
    await waitFor(() => {
      expect(screen.getByText('Новый тестовый комментарий')).toBeInTheDocument();
    });
  });

  test('Изменение статуса дефекта через workflow', async () => {
    const user = userEvent.setup();
    
    // Устанавливаем пользователя как авторизованного менеджера
    localStorage.setItem('token', 'mock-token');
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      username: 'manager',
      role: 'manager'
    }));
    
    // 1. Переходим к деталям дефекта
    renderApp('/defects/1');
    
    await waitFor(() => {
      expect(screen.getByText('Трещина в стене')).toBeInTheDocument();
    });
    
    // 2. Проверяем, что дефект в статусе "Новый"
    expect(screen.getByText('Новый')).toBeInTheDocument();
    
    // 3. Находим кнопку перевода в статус "В работе"
    const inProgressButton = screen.getByRole('button', { name: /перевести в "В работе"/i });
    await user.click(inProgressButton);
    
    // 4. Проверяем, что статус изменился (в реальном приложении)
    // В тестах мы проверяем, что API был вызван
    const { defectsAPI } = require('../../services/api');
    expect(defectsAPI.changeStatus).toHaveBeenCalledWith(1, 'in_progress');
  });

  test('Фильтрация дефектов по статусу', async () => {
    const user = userEvent.setup();
    
    // Устанавливаем авторизованного пользователя
    localStorage.setItem('token', 'mock-token');
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      username: 'manager',
      role: 'manager'
    }));
    
    renderApp('/defects');
    
    await waitFor(() => {
      expect(screen.getByText('Дефекты')).toBeInTheDocument();
    });
    
    // Ждем загрузки дефектов
    await waitFor(() => {
      expect(screen.getByText('Трещина в стене')).toBeInTheDocument();
      expect(screen.getByText('Неработающая розетка')).toBeInTheDocument();
    });
    
    // Открываем фильтр по статусу
    const statusFilter = screen.getByLabelText(/статус/i);
    await user.click(statusFilter);
    
    // Выбираем только статус "Новые"
    const newStatusOption = screen.getByText('Новые');
    await user.click(newStatusOption);
    
    // Закрываем dropdown (клик вне)
    await user.click(document.body);
    
    // Проверяем, что API был вызван с правильными параметрами
    const { defectsAPI } = require('../../services/api');
    await waitFor(() => {
      expect(defectsAPI.getDefects).toHaveBeenCalledWith(
        expect.objectContaining({
          status: ['new']
        })
      );
    });
  });

  test('Поиск дефектов', async () => {
    const user = userEvent.setup();
    
    localStorage.setItem('token', 'mock-token');
    localStorage.setItem('user', JSON.stringify({
      id: 1,
      username: 'manager',
      role: 'manager'
    }));
    
    renderApp('/defects');
    
    await waitFor(() => {
      expect(screen.getByText('Дефекты')).toBeInTheDocument();
    });
    
    // Вводим поисковый запрос
    const searchInput = screen.getByPlaceholderText(/поиск дефектов/i);
    await user.type(searchInput, 'трещина');
    
    // Ждем выполнения поиска (обычно с debounce)
    await waitFor(() => {
      const { defectsAPI } = require('../../services/api');
      expect(defectsAPI.getDefects).toHaveBeenCalledWith(
        expect.objectContaining({
          search: 'трещина'
        })
      );
    });
  });
});