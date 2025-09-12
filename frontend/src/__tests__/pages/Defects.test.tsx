/**
 * Интеграционные тесты для страницы Defects
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { configureStore } from '@reduxjs/toolkit';

import { Defects } from '../../pages/Defects';
import { theme } from '../../theme';
import authReducer from '../../store/slices/authSlice';
import projectsReducer from '../../store/slices/projectsSlice';
import defectsReducer from '../../store/slices/defectsSlice';

// Мокируем API
jest.mock('../../services/api', () => ({
  defectsAPI: {
    getDefects: jest.fn(() => Promise.resolve({
      results: [
        {
          id: 1,
          defect_number: 'DEF-2024-001',
          title: 'Тестовый дефект',
          description: 'Описание тестового дефекта',
          status: 'new',
          priority: 'medium',
          severity: 'minor',
          project: { id: 1, name: 'Тестовый проект' },
          category: { id: 1, name: 'Тестовая категория', color: '#ff0000' },
          author: { id: 1, first_name: 'Иван', last_name: 'Иванов' },
          location: 'Тестовая локация',
          comments_count: 2,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        }
      ],
      count: 1
    })),
    getCategories: jest.fn(() => Promise.resolve([
      { id: 1, name: 'Тестовая категория', color: '#ff0000' }
    ])),
    getEngineers: jest.fn(() => Promise.resolve([
      { id: 1, first_name: 'Петр', last_name: 'Петров', specialization: 'Тестирование' }
    ])),
    createDefect: jest.fn(),
    updateDefect: jest.fn(),
    deleteDefect: jest.fn(),
    changeStatus: jest.fn(),
    assign: jest.fn()
  },
  projectsAPI: {
    getProjects: jest.fn(() => Promise.resolve({
      results: [
        { id: 1, name: 'Тестовый проект' }
      ],
      count: 1
    }))
  }
}));

// Мокируем react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

const createMockStore = () => configureStore({
  reducer: {
    auth: authReducer,
    projects: projectsReducer,
    defects: defectsReducer,
  },
  preloadedState: {
    auth: {
      user: { id: 1, username: 'manager', role: 'manager' },
      token: 'test-token',
      isAuthenticated: true,
      permissions: ['create_defect', 'update_defect', 'delete_defect']
    },
    projects: {
      projects: [{ id: 1, name: 'Тестовый проект' }],
      totalCount: 1,
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
    }
  }
});

const renderWithProviders = (component: React.ReactElement) => {
  const store = createMockStore();
  return render(
    <Provider store={store}>
      <BrowserRouter>
        <ThemeProvider theme={theme}>
          {component}
        </ThemeProvider>
      </BrowserRouter>
    </Provider>
  );
};

describe('Страница Defects', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('рендерится корректно', async () => {
    renderWithProviders(<Defects />);
    
    expect(screen.getByText('Дефекты')).toBeInTheDocument();
    
    // Ждем загрузки данных
    await waitFor(() => {
      expect(screen.getByText('Тестовый дефект')).toBeInTheDocument();
    });
  });

  test('отображает статистику дефектов', async () => {
    renderWithProviders(<Defects />);
    
    await waitFor(() => {
      expect(screen.getByText(/всего дефектов/i)).toBeInTheDocument();
      expect(screen.getByText(/новые/i)).toBeInTheDocument();
      expect(screen.getByText(/в работе/i)).toBeInTheDocument();
      expect(screen.getByText(/просроченные/i)).toBeInTheDocument();
    });
  });

  test('показывает кнопку создания дефекта', () => {
    renderWithProviders(<Defects />);
    
    expect(screen.getByRole('button', { name: /создать дефект/i })).toBeInTheDocument();
  });

  test('открывает диалог создания дефекта', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Defects />);
    
    const createButton = screen.getByRole('button', { name: /создать дефект/i });
    await user.click(createButton);
    
    await waitFor(() => {
      expect(screen.getByText('Создать дефект')).toBeInTheDocument();
    });
  });

  test('отображает таблицу дефектов', async () => {
    renderWithProviders(<Defects />);
    
    await waitFor(() => {
      expect(screen.getByText('DEF-2024-001')).toBeInTheDocument();
      expect(screen.getByText('Тестовый дефект')).toBeInTheDocument();
      expect(screen.getByText('Тестовая локация')).toBeInTheDocument();
    });
  });

  test('позволяет фильтровать дефекты по статусу', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Defects />);
    
    // Открываем фильтр статусов
    const statusFilter = screen.getByLabelText(/статус/i);
    await user.click(statusFilter);
    
    // Выбираем статус "новые"
    const newStatusOption = screen.getByRole('option', { name: /новые/i });
    await user.click(newStatusOption);
    
    // Проверяем что фильтр применился
    await waitFor(() => {
      // Тут должна быть логика проверки применения фильтра
      expect(statusFilter).toHaveValue('new');
    });
  });

  test('позволяет искать дефекты', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Defects />);
    
    const searchInput = screen.getByPlaceholderText(/поиск дефектов/i);
    await user.type(searchInput, 'тестовый');
    
    // Ждем применения поиска
    await waitFor(() => {
      expect(searchInput).toHaveValue('тестовый');
    });
  });

  test('показывает меню действий для дефекта', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Defects />);
    
    await waitFor(() => {
      expect(screen.getByText('Тестовый дефект')).toBeInTheDocument();
    });
    
    // Кликаем на кнопку меню действий
    const actionButton = screen.getByRole('button', { name: /действия/i });
    await user.click(actionButton);
    
    await waitFor(() => {
      expect(screen.getByText(/редактировать/i)).toBeInTheDocument();
      expect(screen.getByText(/удалить/i)).toBeInTheDocument();
    });
  });

  test('навигация к деталям дефекта при клике на строку', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Defects />);
    
    await waitFor(() => {
      expect(screen.getByText('Тестовый дефект')).toBeInTheDocument();
    });
    
    // Кликаем на строку с дефектом
    const defectRow = screen.getByText('Тестовый дефект').closest('tr');
    await user.click(defectRow!);
    
    expect(mockNavigate).toHaveBeenCalledWith('/defects/1');
  });

  test('показывает пагинацию', async () => {
    renderWithProviders(<Defects />);
    
    await waitFor(() => {
      expect(screen.getByText(/строк на странице/i)).toBeInTheDocument();
    });
  });

  test('отображает сообщение когда нет дефектов', async () => {
    // Мокируем пустой ответ API
    const { defectsAPI } = require('../../services/api');
    defectsAPI.getDefects.mockResolvedValueOnce({ results: [], count: 0 });
    
    renderWithProviders(<Defects />);
    
    await waitFor(() => {
      expect(screen.getByText(/дефектов не найдено/i)).toBeInTheDocument();
    });
  });

  test('показывает индикатор загрузки', () => {
    // Мокируем медленную загрузку
    const { defectsAPI } = require('../../services/api');
    defectsAPI.getDefects.mockImplementation(() => new Promise(resolve => 
      setTimeout(() => resolve({ results: [], count: 0 }), 1000)
    ));
    
    renderWithProviders(<Defects />);
    
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  test('обрабатывает ошибку загрузки', async () => {
    // Мокируем ошибку API
    const { defectsAPI } = require('../../services/api');
    defectsAPI.getDefects.mockRejectedValueOnce(new Error('Ошибка сети'));
    
    renderWithProviders(<Defects />);
    
    await waitFor(() => {
      expect(screen.getByText(/ошибка загрузки/i)).toBeInTheDocument();
    });
  });
});