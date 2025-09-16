/**
 * Тесты для компонента DefectDialogs
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Provider } from 'react-redux';
import { ThemeProvider } from '@mui/material/styles';
import { configureStore } from '@reduxjs/toolkit';

import { CreateDefectDialog, EditDefectDialog, StatusChangeDialog, AssignDefectDialog } from '../../components/defects/DefectDialogs';
import { theme } from '../../theme';
import authReducer from '../../store/slices/authSlice';
import { Defect } from '../../types';

// Mock store
const createMockStore = () => configureStore({
  reducer: {
    auth: authReducer,
  },
  preloadedState: {
    auth: {
      user: { id: 1, username: 'test', role: 'manager' },
      token: 'test-token',
      isAuthenticated: true,
    }
  }
});

// Mock defect data
const mockDefect: Defect = {
  id: 1,
  defect_number: 'DEF-2024-001',
  title: 'Test Defect',
  description: 'Test Description',
  status: 'new',
  priority: 'medium',
  severity: 'minor',
  project: { id: 1, name: 'Test Project' },
  category: { id: 1, name: 'Test Category', color: '#ff0000' },
  author: { id: 1, first_name: 'John', last_name: 'Doe' },
  location: 'Test Location',
  comments_count: 0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
};

const renderWithProviders = (component: React.ReactElement) => {
  const store = createMockStore();
  return render(
    <Provider store={store}>
      <ThemeProvider theme={theme}>
        {component}
      </ThemeProvider>
    </Provider>
  );
};

describe('DefectDialogs', () => {
  describe('CreateDefectDialog', () => {
    const defaultProps = {
      open: true,
      onClose: jest.fn(),
      onSubmit: jest.fn(),
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('рендерится корректно', () => {
      renderWithProviders(<CreateDefectDialog {...defaultProps} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Создать дефект')).toBeInTheDocument();
    });

    test('содержит все необходимые поля', () => {
      renderWithProviders(<CreateDefectDialog {...defaultProps} />);
      
      expect(screen.getByLabelText(/название/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/описание/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/проект/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/категория/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/приоритет/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/серьезность/i)).toBeInTheDocument();
    });

    test('валидирует обязательные поля', async () => {
      const user = userEvent.setup();
      renderWithProviders(<CreateDefectDialog {...defaultProps} />);
      
      const submitButton = screen.getByRole('button', { name: /создать/i });
      await user.click(submitButton);
      
      // Проверяем, что форма не отправилась без заполненных полей
      expect(defaultProps.onSubmit).not.toHaveBeenCalled();
    });

    test('отправляет данные при корректном заполнении', async () => {
      const user = userEvent.setup();
      renderWithProviders(<CreateDefectDialog {...defaultProps} />);
      
      // Заполняем обязательные поля
      await user.type(screen.getByLabelText(/название/i), 'Test Defect');
      await user.type(screen.getByLabelText(/описание/i), 'Test Description');
      
      const submitButton = screen.getByRole('button', { name: /создать/i });
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(defaultProps.onSubmit).toHaveBeenCalled();
      });
    });

    test('закрывается при нажатии отмена', async () => {
      const user = userEvent.setup();
      renderWithProviders(<CreateDefectDialog {...defaultProps} />);
      
      const cancelButton = screen.getByRole('button', { name: /отмена/i });
      await user.click(cancelButton);
      
      expect(defaultProps.onClose).toHaveBeenCalled();
    });
  });

  describe('EditDefectDialog', () => {
    const defaultProps = {
      open: true,
      onClose: jest.fn(),
      onSubmit: jest.fn(),
      defect: mockDefect,
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('рендерится с данными дефекта', () => {
      renderWithProviders(<EditDefectDialog {...defaultProps} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText('Редактировать дефект')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Test Defect')).toBeInTheDocument();
    });

    test('сохраняет изменения', async () => {
      const user = userEvent.setup();
      renderWithProviders(<EditDefectDialog {...defaultProps} />);
      
      const titleInput = screen.getByDisplayValue('Test Defect');
      await user.clear(titleInput);
      await user.type(titleInput, 'Updated Defect');
      
      const saveButton = screen.getByRole('button', { name: /сохранить/i });
      await user.click(saveButton);
      
      await waitFor(() => {
        expect(defaultProps.onSubmit).toHaveBeenCalled();
      });
    });
  });

  describe('StatusChangeDialog', () => {
    const defaultProps = {
      open: true,
      onClose: jest.fn(),
      onSubmit: jest.fn(),
      defect: mockDefect,
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('отображает текущий статус', () => {
      renderWithProviders(<StatusChangeDialog {...defaultProps} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/изменить статус/i)).toBeInTheDocument();
    });

    test('позволяет выбрать новый статус', async () => {
      const user = userEvent.setup();
      renderWithProviders(<StatusChangeDialog {...defaultProps} />);
      
      // Выбираем статус "В работе"
      const statusButton = screen.getByRole('button', { name: /в работе/i });
      await user.click(statusButton);
      
      const confirmButton = screen.getByRole('button', { name: /изменить статус/i });
      await user.click(confirmButton);
      
      await waitFor(() => {
        expect(defaultProps.onSubmit).toHaveBeenCalledWith('in_progress', expect.any(String));
      });
    });
  });

  describe('AssignDefectDialog', () => {
    const defaultProps = {
      open: true,
      onClose: jest.fn(),
      onSubmit: jest.fn(),
      defect: mockDefect,
    };

    beforeEach(() => {
      jest.clearAllMocks();
    });

    test('рендерится корректно', () => {
      renderWithProviders(<AssignDefectDialog {...defaultProps} />);
      
      expect(screen.getByRole('dialog')).toBeInTheDocument();
      expect(screen.getByText(/назначить исполнителя/i)).toBeInTheDocument();
    });

    test('содержит поле для выбора исполнителя', () => {
      renderWithProviders(<AssignDefectDialog {...defaultProps} />);
      
      expect(screen.getByLabelText(/исполнитель/i)).toBeInTheDocument();
    });

    test('назначает исполнителя', async () => {
      const user = userEvent.setup();
      renderWithProviders(<AssignDefectDialog {...defaultProps} />);
      
      const assignButton = screen.getByRole('button', { name: /назначить/i });
      await user.click(assignButton);
      
      await waitFor(() => {
        expect(defaultProps.onSubmit).toHaveBeenCalled();
      });
    });
  });
});