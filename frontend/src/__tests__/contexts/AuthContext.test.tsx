/**
 * Тесты для AuthContext
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';

import { AuthProvider, useAuth } from '../../contexts/AuthContext';
import { authAPI } from '../../services/api';

// Мокируем API
jest.mock('../../services/api', () => ({
  authAPI: {
    login: jest.fn(),
    logout: jest.fn(() => Promise.resolve({ success: true })),
    getCurrentUser: jest.fn()
  }
}));

// Мокируем localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn()
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Тестовый компонент для проверки контекста
const TestComponent: React.FC = () => {
  const {
    user,
    isAuthenticated,
    login,
    logout,
    hasPermission,
    isLoading
  } = useAuth();

  return (
    <div>
      <div data-testid="authenticated">{isAuthenticated ? 'true' : 'false'}</div>
      <div data-testid="loading">{isLoading ? 'true' : 'false'}</div>
      <div data-testid="username">{user?.username || 'none'}</div>
      <div data-testid="role">{user?.role || 'none'}</div>
      <div data-testid="can-create">{hasPermission('create_project') ? 'true' : 'false'}</div>
      
      <button onClick={() => login('manager', 'password')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  test('предоставляет начальное состояние', () => {
    renderWithRouter(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('username')).toHaveTextContent('none');
    expect(screen.getByTestId('role')).toHaveTextContent('none');
  });

  test('восстанавливает пользователя из localStorage', async () => {
    const mockUser = {
      id: 1,
      username: 'manager',
      role: 'manager',
      first_name: 'Анна',
      last_name: 'Менеджерова'
    };
    
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'user') return JSON.stringify(mockUser);
      if (key === 'token') return 'mock-token';
      return null;
    });

    (authAPI.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

    await act(async () => {
      renderWithRouter(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
    });

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('username')).toHaveTextContent('manager');
      expect(screen.getByTestId('role')).toHaveTextContent('manager');
    });
  });

  test('выполняет успешный вход', async () => {
    const user = userEvent.setup();
    const mockResponse = {
      token: 'mock-token',
      user: {
        id: 1,
        username: 'manager',
        role: 'manager',
        first_name: 'Анна',
        last_name: 'Менеджерова'
      }
    };

    (authAPI.login as jest.Mock).mockResolvedValue(mockResponse);

    renderWithRouter(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    await user.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
      expect(screen.getByTestId('username')).toHaveTextContent('manager');
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', expect.any(String));
    expect(localStorageMock.setItem).toHaveBeenCalledWith('user', expect.any(String));
  });

  test('обрабатывает ошибку входа', async () => {
    const user = userEvent.setup();
    
    (authAPI.login as jest.Mock).mockRejectedValue(new Error('Invalid credentials'));

    renderWithRouter(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    const loginButton = screen.getByText('Login');
    await user.click(loginButton);

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    });
  });

  test('выполняет выход', async () => {
    const user = userEvent.setup();
    
    // Устанавливаем начальное состояние - пользователь авторизован
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'user') return JSON.stringify({ id: 1, username: 'manager', role: 'manager' });
      if (key === 'token') return 'mock-token';
      return null;
    });

    (authAPI.getCurrentUser as jest.Mock).mockResolvedValue({ id: 1, username: 'manager', role: 'manager' });

    await act(async () => {
      renderWithRouter(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
    });

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });

    const logoutButton = screen.getByText('Logout');
    await user.click(logoutButton);

    await waitFor(() => {
      expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
      expect(screen.getByTestId('username')).toHaveTextContent('none');
    });

    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('user');
  });

  test('проверяет разрешения для менеджера', async () => {
    const mockUser = {
      id: 1,
      username: 'manager',
      role: 'manager',
      first_name: 'Анна',
      last_name: 'Менеджерова'
    };
    
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'user') return JSON.stringify(mockUser);
      if (key === 'token') return 'mock-token';
      return null;
    });

    (authAPI.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

    await act(async () => {
      renderWithRouter(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
    });

    await waitFor(() => {
      expect(screen.getByTestId('can-create')).toHaveTextContent('true');
    });
  });

  test('ограничивает разрешения для observer', async () => {
    const mockUser = {
      id: 3,
      username: 'observer',
      role: 'observer',
      first_name: 'Мария',
      last_name: 'Наблюдательева'
    };
    
    localStorageMock.getItem.mockImplementation((key) => {
      if (key === 'user') return JSON.stringify(mockUser);
      if (key === 'token') return 'mock-token';
      return null;
    });

    (authAPI.getCurrentUser as jest.Mock).mockResolvedValue(mockUser);

    await act(async () => {
      renderWithRouter(
        <AuthProvider>
          <TestComponent />
        </AuthProvider>
      );
    });

    await waitFor(() => {
      expect(screen.getByTestId('role')).toHaveTextContent('observer');
      expect(screen.getByTestId('can-create')).toHaveTextContent('false');
    });
  });

  test('показывает состояние загрузки', async () => {
    let resolveAuth: () => void;
    (authAPI.getCurrentUser as jest.Mock).mockImplementation(() => 
      new Promise(resolve => {
        resolveAuth = () => resolve(null);
        // Не резолвим сразу, чтобы увидеть состояние загрузки
      })
    );

    renderWithRouter(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Даем время для инициализации состояния загрузки
    await new Promise(resolve => setTimeout(resolve, 10));

    expect(screen.getByTestId('loading')).toHaveTextContent('true');

    // Теперь резолвим промис
    act(() => {
      resolveAuth();
    });

    await waitFor(() => {
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
    });
  });
});