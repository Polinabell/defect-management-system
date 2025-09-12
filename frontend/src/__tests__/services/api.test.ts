/**
 * Тесты для API сервисов
 */

import { defectsAPI, projectsAPI, authAPI, commentsAPI } from '../../services/api';

// Mock для fetch
global.fetch = jest.fn();

describe('API Services', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('authAPI', () => {
    test('login возвращает пользователя при правильных учетных данных', async () => {
      const credentials = { username: 'manager', password: 'password' };
      
      const result = await authAPI.login(credentials);
      
      expect(result).toHaveProperty('token');
      expect(result).toHaveProperty('user');
      expect(result.user.username).toBe('manager');
      expect(result.user.role).toBe('manager');
    });

    test('login выбрасывает ошибку при неправильных учетных данных', async () => {
      const credentials = { username: 'wrong', password: 'wrong' };
      
      await expect(authAPI.login(credentials)).rejects.toThrow('Invalid credentials');
    });

    test('getCurrentUser возвращает пользователя из localStorage', async () => {
      const mockUser = { id: 1, username: 'test', role: 'manager' };
      localStorage.setItem('user', JSON.stringify(mockUser));
      
      const result = await authAPI.getCurrentUser();
      
      expect(result).toEqual(mockUser);
    });

    test('getCurrentUser выбрасывает ошибку если пользователя нет', async () => {
      localStorage.removeItem('user');
      
      await expect(authAPI.getCurrentUser()).rejects.toThrow('User not found');
    });

    test('logout возвращает success', async () => {
      const result = await authAPI.logout();
      
      expect(result.success).toBe(true);
    });
  });

  describe('projectsAPI', () => {
    test('getProjects возвращает список проектов', async () => {
      const result = await projectsAPI.getProjects();
      
      expect(result).toHaveProperty('results');
      expect(result).toHaveProperty('count');
      expect(Array.isArray(result.results)).toBe(true);
      expect(result.results.length).toBeGreaterThan(0);
    });

    test('getProjects фильтрует по поисковому запросу', async () => {
      const result = await projectsAPI.getProjects({ search: 'Север' });
      
      expect(result.results).toHaveLength(1);
      expect(result.results[0].name).toContain('Север');
    });

    test('getProjects фильтрует по статусу', async () => {
      const result = await projectsAPI.getProjects({ status: ['in_progress'] });
      
      result.results.forEach(project => {
        expect(project.status).toBe('in_progress');
      });
    });

    test('getProject возвращает конкретный проект', async () => {
      const result = await projectsAPI.getProject(1);
      
      expect(result.id).toBe(1);
      expect(result.name).toBe('Жилой комплекс "Север"');
    });

    test('getProject выбрасывает ошибку для несуществующего проекта', async () => {
      await expect(projectsAPI.getProject(999)).rejects.toThrow('Проект не найден');
    });

    test('createProject создает новый проект', async () => {
      const projectData = new FormData();
      projectData.append('name', 'Новый проект');
      projectData.append('description', 'Описание нового проекта');
      
      const result = await projectsAPI.createProject(projectData);
      
      expect(result.name).toBe('Новый проект');
      expect(result.description).toBe('Описание нового проекта');
    });

    test('updateProject обновляет существующий проект', async () => {
      const updateData = { name: 'Обновленное название' };
      
      const result = await projectsAPI.updateProject(1, updateData);
      
      expect(result.name).toBe('Обновленное название');
    });

    test('deleteProject удаляет проект', async () => {
      await expect(projectsAPI.deleteProject(1)).resolves.not.toThrow();
    });
  });

  describe('defectsAPI', () => {
    test('getDefects возвращает список дефектов', async () => {
      const result = await defectsAPI.getDefects();
      
      expect(result).toHaveProperty('results');
      expect(result).toHaveProperty('count');
      expect(Array.isArray(result.results)).toBe(true);
    });

    test('getDefects фильтрует по статусу', async () => {
      const result = await defectsAPI.getDefects({ status: ['new'] });
      
      result.results.forEach(defect => {
        expect(defect.status).toBe('new');
      });
    });

    test('getDefects фильтрует по приоритету', async () => {
      const result = await defectsAPI.getDefects({ priority: ['high'] });
      
      result.results.forEach(defect => {
        expect(defect.priority).toBe('high');
      });
    });

    test('getDefect возвращает конкретный дефект', async () => {
      const result = await defectsAPI.getDefect(1);
      
      expect(result.id).toBe(1);
      expect(result).toHaveProperty('defect_number');
    });

    test('createDefect создает новый дефект', async () => {
      const defectData = new FormData();
      defectData.append('title', 'Новый дефект');
      defectData.append('description', 'Описание дефекта');
      
      const result = await defectsAPI.createDefect(defectData);
      
      expect(result.title).toBe('Новый дефект');
      expect(result.status).toBe('new');
    });

    test('updateDefect обновляет дефект', async () => {
      const updateData = { title: 'Обновленный дефект' };
      
      const result = await defectsAPI.updateDefect(1, updateData);
      
      expect(result.title).toBe('Обновленный дефект');
    });

    test('changeStatus изменяет статус дефекта', async () => {
      const result = await defectsAPI.changeStatus(1, 'in_progress');
      
      expect(result.status).toBe('in_progress');
    });

    test('changeStatus отклоняет недопустимый статус', async () => {
      await expect(defectsAPI.changeStatus(1, 'invalid_status')).rejects.toThrow('Недопустимый статус');
    });

    test('assign назначает исполнителя', async () => {
      const result = await defectsAPI.assign(1, 2, '2024-12-31');
      
      expect(result.assignee?.id).toBe(2);
      expect(result.due_date).toBe('2024-12-31');
    });

    test('getCategories возвращает список категорий', async () => {
      const result = await defectsAPI.getCategories();
      
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty('name');
      expect(result[0]).toHaveProperty('color');
    });

    test('getEngineers возвращает список инженеров', async () => {
      const result = await defectsAPI.getEngineers();
      
      expect(Array.isArray(result)).toBe(true);
      expect(result.length).toBeGreaterThan(0);
      expect(result[0]).toHaveProperty('first_name');
      expect(result[0]).toHaveProperty('specialization');
    });
  });

  describe('commentsAPI', () => {
    test('getDefectComments возвращает комментарии для дефекта', async () => {
      const result = await commentsAPI.getDefectComments(1);
      
      expect(Array.isArray(result)).toBe(true);
      result.forEach(comment => {
        expect(comment.defect_id).toBe(1);
        expect(comment).toHaveProperty('author');
        expect(comment).toHaveProperty('content');
      });
    });

    test('addComment добавляет новый комментарий', async () => {
      const content = 'Тестовый комментарий';
      
      const result = await commentsAPI.addComment(1, content);
      
      expect(result.content).toBe(content);
      expect(result.defect_id).toBe(1);
      expect(result.is_internal).toBe(false);
    });

    test('addComment добавляет внутренний комментарий', async () => {
      const content = 'Внутренний комментарий';
      
      const result = await commentsAPI.addComment(1, content, true);
      
      expect(result.is_internal).toBe(true);
    });

    test('addComment с файлами', async () => {
      const content = 'Комментарий с файлом';
      const files = new DataTransfer();
      files.items.add(new File(['test'], 'test.txt', { type: 'text/plain' }));
      
      const result = await commentsAPI.addComment(1, content, false, files.files);
      
      expect(result.attachments).toHaveLength(1);
      expect(result.attachments[0].filename).toBe('test.txt');
    });

    test('updateComment обновляет комментарий', async () => {
      const newContent = 'Обновленный комментарий';
      
      const result = await commentsAPI.updateComment(1, newContent);
      
      expect(result.content).toBe(newContent);
    });

    test('deleteComment удаляет комментарий', async () => {
      await expect(commentsAPI.deleteComment(1)).resolves.not.toThrow();
    });
  });
});