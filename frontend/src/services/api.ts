/**
 * API сервисы для взаимодействия с backend
 */

import { Project } from '../store/slices/projectsSlice';
import { Defect } from '../store/slices/defectsSlice';

// Mock данные для проектов
const MOCK_PROJECTS: Project[] = [
  {
    id: 1,
    name: 'Жилой комплекс "Север"',
    description: 'Строительство многоэтажного жилого комплекса на 200 квартир',
    status: 'in_progress',
    priority: 'high',
    manager: {
      id: 1,
      first_name: 'Анна',
      last_name: 'Менеджерова'
    },
    start_date: '2024-01-15',
    end_date: '2024-12-20',
    progress_percentage: 45,
    defects_count: 12,
    members_count: 15,
    created_at: '2024-01-10T10:00:00Z',
    updated_at: '2024-01-20T14:30:00Z'
  },
  {
    id: 2,
    name: 'Торговый центр "Восток"',
    description: 'Реконструкция торгового центра с расширением торговых площадей',
    status: 'planning',
    priority: 'medium',
    manager: {
      id: 1,
      first_name: 'Анна',
      last_name: 'Менеджерова'
    },
    start_date: '2024-02-01',
    end_date: '2024-08-15',
    progress_percentage: 5,
    defects_count: 3,
    members_count: 8,
    created_at: '2024-01-25T09:00:00Z',
    updated_at: '2024-01-26T16:45:00Z'
  },
  {
    id: 3,
    name: 'Офисное здание "Центр"',
    description: 'Строительство 12-этажного офисного здания класса A',
    status: 'completed',
    priority: 'low',
    manager: {
      id: 2,
      first_name: 'Петр',
      last_name: 'Инженеров'
    },
    start_date: '2023-06-01',
    end_date: '2024-01-15',
    progress_percentage: 100,
    defects_count: 0,
    members_count: 12,
    created_at: '2023-05-20T11:00:00Z',
    updated_at: '2024-01-15T17:00:00Z'
  }
];

// Mock данные для дефектов
const MOCK_DEFECTS: Defect[] = [
  {
    id: 1,
    defect_number: 'DEF-2024-001',
    title: 'Трещины в бетонной стене на 5-м этаже',
    description: 'Обнаружены вертикальные трещины в несущей стене. Требуется немедленное вмешательство для оценки структурной целостности.',
    status: 'new',
    priority: 'high',
    severity: 'major',
    project: { id: 1, name: 'Жилой комплекс "Север"' },
    category: { id: 1, name: 'Структурные дефекты', color: '#f44336' },
    author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
    assignee: { id: 2, first_name: 'Петр', last_name: 'Инженеров' },
    location: 'Здание A, секция 1',
    floor: '5',
    room: 'Квартира 501',
    due_date: '2024-09-15',
    is_overdue: false,
    days_remaining: 7,
    main_image: {
      id: 1,
      file_url: '/images/defects/crack-wall-1.jpg',
      filename: 'crack-wall-1.jpg'
    },
    comments_count: 3,
    created_at: '2024-09-01T10:00:00Z',
    updated_at: '2024-09-05T14:30:00Z'
  },
  {
    id: 2,
    defect_number: 'DEF-2024-002',
    title: 'Неисправность электрической розетки',
    description: 'Розетка в спальне искрит при подключении приборов. Потенциальная угроза пожара.',
    status: 'in_progress',
    priority: 'critical',
    severity: 'critical',
    project: { id: 1, name: 'Жилой комплекс "Север"' },
    category: { id: 2, name: 'Электрические проблемы', color: '#ff9800' },
    author: { id: 2, first_name: 'Петр', last_name: 'Инженеров' },
    assignee: { id: 3, first_name: 'Мария', last_name: 'Электрикова' },
    location: 'Здание B, секция 2',
    floor: '3',
    room: 'Квартира 302',
    due_date: '2024-09-10',
    is_overdue: true,
    days_remaining: -2,
    main_image: {
      id: 2,
      file_url: '/images/defects/electrical-outlet.jpg',
      filename: 'electrical-outlet.jpg'
    },
    comments_count: 8,
    created_at: '2024-08-28T09:15:00Z',
    updated_at: '2024-09-08T11:20:00Z'
  },
  {
    id: 3,
    defect_number: 'DEF-2024-003',
    title: 'Протечка в санузле',
    description: 'Обнаружена протечка воды в районе стояка холодной воды. Повреждение может распространиться на нижние этажи.',
    status: 'review',
    priority: 'high',
    severity: 'major',
    project: { id: 1, name: 'Жилой комплекс "Север"' },
    category: { id: 3, name: 'Сантехнические дефекты', color: '#2196f3' },
    author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
    assignee: { id: 4, first_name: 'Иван', last_name: 'Сантехников' },
    location: 'Здание A, секция 3',
    floor: '7',
    room: 'Санузел квартиры 705',
    due_date: '2024-09-12',
    is_overdue: false,
    days_remaining: 4,
    comments_count: 5,
    created_at: '2024-09-02T16:45:00Z',
    updated_at: '2024-09-07T13:10:00Z'
  },
  {
    id: 4,
    defect_number: 'DEF-2024-004',
    title: 'Неровность напольного покрытия',
    description: 'Ламинат уложен неровно, образуются зазоры и скрипы при ходьбе.',
    status: 'closed',
    priority: 'medium',
    severity: 'minor',
    project: { id: 1, name: 'Жилой комплекс "Север"' },
    category: { id: 4, name: 'Отделочные работы', color: '#4caf50' },
    author: { id: 2, first_name: 'Петр', last_name: 'Инженеров' },
    assignee: { id: 5, first_name: 'Сергей', last_name: 'Отделочников' },
    location: 'Здание C, секция 1',
    floor: '2',
    room: 'Гостиная квартиры 201',
    due_date: '2024-08-30',
    is_overdue: false,
    main_image: {
      id: 3,
      file_url: '/images/defects/floor-defect.jpg',
      filename: 'floor-defect.jpg'
    },
    comments_count: 2,
    created_at: '2024-08-20T11:30:00Z',
    updated_at: '2024-08-30T17:45:00Z'
  },
  {
    id: 5,
    defect_number: 'DEF-2024-005',
    title: 'Отсутствие ограждения на балконе',
    description: 'Балкон на 8-м этаже не имеет установленного ограждения, что создает угрозу безопасности.',
    status: 'new',
    priority: 'critical',
    severity: 'blocking',
    project: { id: 1, name: 'Жилой комплекс "Север"' },
    category: { id: 5, name: 'Безопасность', color: '#e91e63' },
    author: { id: 3, first_name: 'Мария', last_name: 'Наблюдательева' },
    location: 'Здание D, секция 1',
    floor: '8',
    room: 'Балкон квартиры 801',
    due_date: '2024-09-09',
    is_overdue: true,
    days_remaining: -1,
    comments_count: 1,
    created_at: '2024-09-07T08:20:00Z',
    updated_at: '2024-09-07T08:20:00Z'
  },
  {
    id: 6,
    defect_number: 'DEF-2024-006',
    title: 'Неисправность вентиляционной системы',
    description: 'Вентиляционные решетки забиты строительным мусором, нарушена циркуляция воздуха.',
    status: 'in_progress',
    priority: 'medium',
    severity: 'major',
    project: { id: 2, name: 'Торговый центр "Восток"' },
    category: { id: 6, name: 'Вентиляция и кондиционирование', color: '#607d8b' },
    author: { id: 2, first_name: 'Петр', last_name: 'Инженеров' },
    assignee: { id: 6, first_name: 'Алексей', last_name: 'Вентиляционщик' },
    location: 'Основное здание',
    floor: '2',
    room: 'Торговый зал секция A',
    due_date: '2024-09-20',
    is_overdue: false,
    days_remaining: 12,
    comments_count: 4,
    created_at: '2024-09-03T14:00:00Z',
    updated_at: '2024-09-06T16:30:00Z'
  },
  {
    id: 7,
    defect_number: 'DEF-2024-007',
    title: 'Царапины на стеклянных перегородках',
    description: 'Множественные царапины на стеклянных перегородках в офисной зоне.',
    status: 'cancelled',
    priority: 'low',
    severity: 'cosmetic',
    project: { id: 3, name: 'Офисное здание "Центр"' },
    category: { id: 4, name: 'Отделочные работы', color: '#4caf50' },
    author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
    location: 'Офисный блок A',
    floor: '5',
    room: 'Переговорная 502',
    comments_count: 6,
    created_at: '2024-08-15T12:00:00Z',
    updated_at: '2024-08-25T10:15:00Z'
  },
  {
    id: 8,
    defect_number: 'DEF-2024-008',
    title: 'Неисправность системы пожарной сигнализации',
    description: 'Датчики дыма не реагируют на тестирование, система требует полной диагностики.',
    status: 'new',
    priority: 'critical',
    severity: 'blocking',
    project: { id: 2, name: 'Торговый центр "Восток"' },
    category: { id: 5, name: 'Безопасность', color: '#e91e63' },
    author: { id: 3, first_name: 'Мария', last_name: 'Наблюдательева' },
    assignee: { id: 7, first_name: 'Николай', last_name: 'Пожарников' },
    location: 'Весь комплекс',
    floor: 'Все этажи',
    due_date: '2024-09-11',
    is_overdue: false,
    days_remaining: 3,
    comments_count: 2,
    created_at: '2024-09-05T09:30:00Z',
    updated_at: '2024-09-05T09:30:00Z'
  }
];

// Mock данные для категорий дефектов
const MOCK_DEFECT_CATEGORIES = [
  { id: 1, name: 'Структурные дефекты', color: '#f44336' },
  { id: 2, name: 'Электрические проблемы', color: '#ff9800' },
  { id: 3, name: 'Сантехнические дефекты', color: '#2196f3' },
  { id: 4, name: 'Отделочные работы', color: '#4caf50' },
  { id: 5, name: 'Безопасность', color: '#e91e63' },
  { id: 6, name: 'Вентиляция и кондиционирование', color: '#607d8b' }
];

// Mock данные для инженеров/исполнителей
const MOCK_ENGINEERS = [
  { id: 2, first_name: 'Петр', last_name: 'Инженеров', specialization: 'Конструкции' },
  { id: 3, first_name: 'Мария', last_name: 'Электрикова', specialization: 'Электрика' },
  { id: 4, first_name: 'Иван', last_name: 'Сантехников', specialization: 'Сантехника' },
  { id: 5, first_name: 'Сергей', last_name: 'Отделочников', specialization: 'Отделка' },
  { id: 6, first_name: 'Алексей', last_name: 'Вентиляционщик', specialization: 'Вентиляция' },
  { id: 7, first_name: 'Николай', last_name: 'Пожарников', specialization: 'Пожарная безопасность' }
];

// Типы для API ответов
interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}

// Проекты API
export const projectsAPI = {
  getProjects: async (params: {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: string[];
    priority?: string[];
  } = {}): Promise<PaginatedResponse<Project>> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    let filteredProjects = [...MOCK_PROJECTS];
    
    // Фильтрация по поиску
    if (params.search) {
      filteredProjects = filteredProjects.filter(p => 
        p.name.toLowerCase().includes(params.search!.toLowerCase()) ||
        p.description.toLowerCase().includes(params.search!.toLowerCase())
      );
    }
    
    // Фильтрация по статусу
    if (params.status?.length) {
      filteredProjects = filteredProjects.filter(p => 
        params.status!.includes(p.status)
      );
    }
    
    // Фильтрация по приоритету
    if (params.priority?.length) {
      filteredProjects = filteredProjects.filter(p => 
        params.priority!.includes(p.priority)
      );
    }
    
    const pageSize = params.pageSize || 20;
    const page = params.page || 1;
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    
    return {
      results: filteredProjects.slice(startIndex, endIndex),
      count: filteredProjects.length
    };
  },
  
  getProject: async (id: number): Promise<Project> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const project = MOCK_PROJECTS.find(p => p.id === id);
    if (!project) {
      throw new Error('Проект не найден');
    }
    return project;
  },
  
  createProject: async (data: Partial<Project>): Promise<Project> => {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    const newProject: Project = {
      id: Math.max(...MOCK_PROJECTS.map(p => p.id)) + 1,
      name: data.name || '',
      description: data.description || '',
      status: data.status || 'planning',
      priority: data.priority || 'medium',
      manager: data.manager || { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
      start_date: data.start_date || new Date().toISOString().split('T')[0],
      end_date: data.end_date,
      progress_percentage: 0,
      defects_count: 0,
      members_count: data.members_count || 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    MOCK_PROJECTS.push(newProject);
    return newProject;
  },
  
  updateProject: async (id: number, data: Partial<Project>): Promise<Project> => {
    await new Promise(resolve => setTimeout(resolve, 600));
    
    const index = MOCK_PROJECTS.findIndex(p => p.id === id);
    if (index === -1) {
      throw new Error('Проект не найден');
    }
    
    MOCK_PROJECTS[index] = {
      ...MOCK_PROJECTS[index],
      ...data,
      updated_at: new Date().toISOString()
    };
    
    return MOCK_PROJECTS[index];
  },
  
  deleteProject: async (id: number): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 400));
    
    const index = MOCK_PROJECTS.findIndex(p => p.id === id);
    if (index === -1) {
      throw new Error('Проект не найден');
    }
    
    MOCK_PROJECTS.splice(index, 1);
  }
};

// Дефекты API
export const defectsAPI = {
  getDefects: async (params: {
    page?: number;
    pageSize?: number;
    search?: string;
    status?: string[];
    priority?: string[];
    severity?: string[];
    project?: number;
    category?: number;
    assignee?: number;
    author?: number;
    is_overdue?: boolean;
  } = {}): Promise<PaginatedResponse<Defect>> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    let filteredDefects = [...MOCK_DEFECTS];
    
    // Фильтрация по поиску
    if (params.search) {
      const searchTerm = params.search.toLowerCase();
      filteredDefects = filteredDefects.filter(d => 
        d.title.toLowerCase().includes(searchTerm) ||
        d.description.toLowerCase().includes(searchTerm) ||
        d.defect_number.toLowerCase().includes(searchTerm) ||
        d.location.toLowerCase().includes(searchTerm)
      );
    }
    
    // Фильтрация по статусу
    if (params.status?.length) {
      filteredDefects = filteredDefects.filter(d => 
        params.status!.includes(d.status)
      );
    }
    
    // Фильтрация по приоритету
    if (params.priority?.length) {
      filteredDefects = filteredDefects.filter(d => 
        params.priority!.includes(d.priority)
      );
    }
    
    // Фильтрация по серьезности
    if (params.severity?.length) {
      filteredDefects = filteredDefects.filter(d => 
        params.severity!.includes(d.severity)
      );
    }
    
    // Фильтрация по проекту
    if (params.project) {
      filteredDefects = filteredDefects.filter(d => 
        d.project.id === params.project
      );
    }
    
    // Фильтрация по категории
    if (params.category) {
      filteredDefects = filteredDefects.filter(d => 
        d.category.id === params.category
      );
    }
    
    // Фильтрация по исполнителю
    if (params.assignee) {
      filteredDefects = filteredDefects.filter(d => 
        d.assignee?.id === params.assignee
      );
    }
    
    // Фильтрация по автору
    if (params.author) {
      filteredDefects = filteredDefects.filter(d => 
        d.author.id === params.author
      );
    }
    
    // Фильтрация по просрочке
    if (params.is_overdue !== undefined) {
      filteredDefects = filteredDefects.filter(d => 
        d.is_overdue === params.is_overdue
      );
    }
    
    const pageSize = params.pageSize || 20;
    const page = params.page || 1;
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    
    return {
      results: filteredDefects.slice(startIndex, endIndex),
      count: filteredDefects.length
    };
  },
  
  getDefect: async (id: number): Promise<Defect> => {
    await new Promise(resolve => setTimeout(resolve, 300));
    const defect = MOCK_DEFECTS.find(d => d.id === id);
    if (!defect) {
      throw new Error('Дефект не найден');
    }
    return defect;
  },
  
  createDefect: async (data: FormData): Promise<Defect> => {
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Имитация создания дефекта из FormData
    const formDataObj: any = {};
    for (const [key, value] of data.entries()) {
      formDataObj[key] = value;
    }
    
    const newDefect: Defect = {
      id: Math.max(...MOCK_DEFECTS.map(d => d.id)) + 1,
      defect_number: `DEF-2024-${String(MOCK_DEFECTS.length + 1).padStart(3, '0')}`,
      title: formDataObj.title || '',
      description: formDataObj.description || '',
      status: 'new',
      priority: formDataObj.priority || 'medium',
      severity: formDataObj.severity || 'minor',
      project: MOCK_PROJECTS.find(p => p.id === parseInt(formDataObj.project)) || MOCK_PROJECTS[0],
      category: MOCK_DEFECT_CATEGORIES.find(c => c.id === parseInt(formDataObj.category)) || MOCK_DEFECT_CATEGORIES[0],
      author: { id: 1, first_name: 'Анна', last_name: 'Менеджерова' },
      assignee: formDataObj.assignee ? MOCK_ENGINEERS.find(e => e.id === parseInt(formDataObj.assignee)) : undefined,
      location: formDataObj.location || '',
      floor: formDataObj.floor,
      room: formDataObj.room,
      due_date: formDataObj.due_date,
      is_overdue: false,
      main_image: formDataObj.image ? {
        id: Date.now(),
        file_url: `/images/defects/${formDataObj.image.name}`,
        filename: formDataObj.image.name
      } : undefined,
      comments_count: 0,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    MOCK_DEFECTS.push(newDefect);
    return newDefect;
  },
  
  updateDefect: async (id: number, data: Partial<Defect>): Promise<Defect> => {
    await new Promise(resolve => setTimeout(resolve, 600));
    
    const index = MOCK_DEFECTS.findIndex(d => d.id === id);
    if (index === -1) {
      throw new Error('Дефект не найден');
    }
    
    MOCK_DEFECTS[index] = {
      ...MOCK_DEFECTS[index],
      ...data,
      updated_at: new Date().toISOString()
    };
    
    return MOCK_DEFECTS[index];
  },
  
  deleteDefect: async (id: number): Promise<void> => {
    await new Promise(resolve => setTimeout(resolve, 400));
    
    const index = MOCK_DEFECTS.findIndex(d => d.id === id);
    if (index === -1) {
      throw new Error('Дефект не найден');
    }
    
    MOCK_DEFECTS.splice(index, 1);
  },
  
  changeStatus: async (id: number, status: string, comment?: string): Promise<Defect> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = MOCK_DEFECTS.findIndex(d => d.id === id);
    if (index === -1) {
      throw new Error('Дефект не найден');
    }
    
    // Валидация статуса по workflow
    const validStatuses = ['new', 'in_progress', 'review', 'closed', 'cancelled'];
    if (!validStatuses.includes(status)) {
      throw new Error('Недопустимый статус');
    }
    
    MOCK_DEFECTS[index] = {
      ...MOCK_DEFECTS[index],
      status: status as Defect['status'],
      updated_at: new Date().toISOString()
    };
    
    return MOCK_DEFECTS[index];
  },
  
  assign: async (id: number, assigneeId: number, due_date?: string, comment?: string): Promise<Defect> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const index = MOCK_DEFECTS.findIndex(d => d.id === id);
    if (index === -1) {
      throw new Error('Дефект не найден');
    }
    
    const assignee = MOCK_ENGINEERS.find(e => e.id === assigneeId);
    if (!assignee) {
      throw new Error('Исполнитель не найден');
    }
    
    // Вычисляем количество дней до дедлайна
    let days_remaining: number | undefined;
    let is_overdue = false;
    
    if (due_date) {
      const dueDateTime = new Date(due_date).getTime();
      const currentTime = new Date().getTime();
      days_remaining = Math.ceil((dueDateTime - currentTime) / (1000 * 60 * 60 * 24));
      is_overdue = days_remaining < 0;
    }
    
    MOCK_DEFECTS[index] = {
      ...MOCK_DEFECTS[index],
      assignee: {
        id: assignee.id,
        first_name: assignee.first_name,
        last_name: assignee.last_name
      },
      due_date,
      days_remaining,
      is_overdue,
      updated_at: new Date().toISOString()
    };
    
    return MOCK_DEFECTS[index];
  },
  
  // Дополнительные методы для поддержки UI
  getCategories: async (): Promise<typeof MOCK_DEFECT_CATEGORIES> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    return MOCK_DEFECT_CATEGORIES;
  },
  
  getEngineers: async (): Promise<typeof MOCK_ENGINEERS> => {
    await new Promise(resolve => setTimeout(resolve, 200));
    return MOCK_ENGINEERS;
  }
};

// Отчеты API (заглушки)
export const reportsAPI = {
  getTemplates: async (params: any = {}): Promise<PaginatedResponse<any>> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return { results: [], count: 0 };
  },
  
  getGeneratedReports: async (params: any = {}): Promise<PaginatedResponse<any>> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return { results: [], count: 0 };
  },
  
  generateReport: async (data: any): Promise<any> => {
    await new Promise(resolve => setTimeout(resolve, 1500));
    return { id: Date.now(), ...data, status: 'completed' };
  },
  
  getDashboards: async (): Promise<PaginatedResponse<any>> => {
    await new Promise(resolve => setTimeout(resolve, 400));
    return { results: [], count: 0 };
  },
  
  getProjectAnalytics: async (projectId: number, params: any): Promise<any> => {
    await new Promise(resolve => setTimeout(resolve, 700));
    return { defects_by_status: {}, progress_by_month: {} };
  },
  
  getSystemAnalytics: async (): Promise<any> => {
    await new Promise(resolve => setTimeout(resolve, 600));
    return { total_projects: 3, total_defects: 15, active_projects: 2 };
  },
  
  getChartData: async (params: any): Promise<any> => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return { labels: [], datasets: [] };
  }
};

// Аутентификация API (обновленная версия)
export const authAPI = {
  login: async (credentials: { username: string; password: string }) => {
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const demoUsers = {
      'manager': {
        id: 1,
        username: 'manager',
        email: 'manager@example.com',
        first_name: 'Анна',
        last_name: 'Менеджерова',
        role: 'manager',
        is_active: true,
        created_at: new Date().toISOString()
      },
      'engineer': {
        id: 2,
        username: 'engineer',
        email: 'engineer@example.com',
        first_name: 'Петр',
        last_name: 'Инженеров',
        role: 'engineer',
        is_active: true,
        created_at: new Date().toISOString()
      },
      'observer': {
        id: 3,
        username: 'observer',
        email: 'observer@example.com',
        first_name: 'Мария',
        last_name: 'Наблюдательева',
        role: 'observer',
        is_active: true,
        created_at: new Date().toISOString()
      }
    };
    
    if (credentials.password === 'password' && demoUsers[credentials.username as keyof typeof demoUsers]) {
      const user = demoUsers[credentials.username as keyof typeof demoUsers];
      return {
        token: `mock_token_${user.id}`,
        user
      };
    }
    
    throw new Error('Invalid credentials');
  },
  
  logout: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    return { success: true };
  },
  
  getCurrentUser: async () => {
    await new Promise(resolve => setTimeout(resolve, 500));
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      return JSON.parse(savedUser);
    }
    throw new Error('User not found');
  }
};