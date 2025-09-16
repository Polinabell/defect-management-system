/**
 * Тесты для компонента DefectWorkflow
 */

import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ThemeProvider } from '@mui/material/styles';

import { DefectWorkflow } from '../../components/defects/DefectWorkflow';
import { theme } from '../../theme';
import { Defect } from '../../types';

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
  reporter: { id: 1, first_name: 'John', last_name: 'Doe' },
  location: 'Test Location',
  comments_count: 0,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
};

const renderWithTheme = (component: React.ReactElement) => {
  return render(
    <ThemeProvider theme={theme}>
      {component}
    </ThemeProvider>
  );
};

describe('DefectWorkflow', () => {
  const defaultProps = {
    defect: mockDefect,
    onStatusChange: jest.fn(),
    canManageDefects: true,
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('рендерится корректно', () => {
    renderWithTheme(<DefectWorkflow {...defaultProps} />);
    
    expect(screen.getByText(/workflow дефекта #1/i)).toBeInTheDocument();
    expect(screen.getAllByText('Новый').length).toBeGreaterThan(0);
  });

  test('отображает текущий статус', () => {
    renderWithTheme(<DefectWorkflow {...defaultProps} />);
    
    expect(screen.getAllByText('Текущий статус').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Новый').length).toBeGreaterThan(0);
  });

  test('показывает все этапы workflow', () => {
    renderWithTheme(<DefectWorkflow {...defaultProps} />);
    
    expect(screen.getAllByText('Новый').length).toBeGreaterThan(0);
    expect(screen.getByText('В работе')).toBeInTheDocument();
    expect(screen.getByText('На проверке')).toBeInTheDocument();
    expect(screen.getByText('Закрыт')).toBeInTheDocument();
  });

  test('отображает доступные действия для менеджера', () => {
    renderWithTheme(<DefectWorkflow {...defaultProps} />);
    
    expect(screen.getByText('Доступные действия')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /перевести в "В работе"/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /перевести в "Отменён"/i })).toBeInTheDocument();
  });

  test('скрывает действия для пользователя без прав', () => {
    renderWithTheme(<DefectWorkflow {...defaultProps} canManageDefects={false} />);
    
    expect(screen.queryByText('Доступные действия')).not.toBeInTheDocument();
  });

  test('вызывает onStatusChange при клике на кнопку действия', async () => {
    const user = userEvent.setup();
    renderWithTheme(<DefectWorkflow {...defaultProps} />);
    
    const inProgressButton = screen.getByRole('button', { name: /перевести в "В работе"/i });
    await user.click(inProgressButton);
    
    expect(defaultProps.onStatusChange).toHaveBeenCalledWith(1, 'in_progress');
  });

  test('отображает правильные переходы для статуса "в работе"', () => {
    const inProgressDefect = { ...mockDefect, status: 'in_progress' };
    renderWithTheme(<DefectWorkflow {...defaultProps} defect={inProgressDefect} />);
    
    expect(screen.getByRole('button', { name: /перевести в "На проверке"/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /перевести в "Отменён"/i })).toBeInTheDocument();
  });

  test('отображает историю изменений', () => {
    renderWithTheme(<DefectWorkflow {...defaultProps} />);
    
    expect(screen.getByText('История изменений')).toBeInTheDocument();
    expect(screen.getByText(/создан пользователем/i)).toBeInTheDocument();
  });

  test('корректно обрабатывает дефект с исполнителем', () => {
    const defectWithAssignee = {
      ...mockDefect,
      assignee: { id: 2, first_name: 'Jane', last_name: 'Smith' }
    };
    
    renderWithTheme(<DefectWorkflow {...defaultProps} defect={defectWithAssignee} />);
    
    expect(screen.getByText(/назначен на Jane Smith/i)).toBeInTheDocument();
  });

  test('правильно отображает статус "закрыт"', () => {
    const closedDefect = { ...mockDefect, status: 'closed' };
    renderWithTheme(<DefectWorkflow {...defaultProps} defect={closedDefect} />);
    
    expect(screen.getByRole('button', { name: /переоткрыть/i })).toBeInTheDocument();
  });

  test('правильно отображает статус "отменён"', () => {
    const cancelledDefect = { ...mockDefect, status: 'cancelled' };
    renderWithTheme(<DefectWorkflow {...defaultProps} defect={cancelledDefect} />);
    
    expect(screen.getByRole('button', { name: /восстановить/i })).toBeInTheDocument();
  });
});