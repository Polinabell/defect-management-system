/**
 * Типы данных приложения
 */

export interface User {
  id: number;
  username: string;
  email?: string;
  first_name: string;
  last_name: string;
  role: 'manager' | 'engineer' | 'observer';
  is_active?: boolean;
  created_at?: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  status: 'planning' | 'in_progress' | 'completed' | 'on_hold' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  manager: User;
  start_date?: string;
  end_date?: string;
  progress_percentage?: number;
  defects_count?: number;
  members_count?: number;
  created_at: string;
  updated_at: string;
}

export interface DefectCategory {
  id: number;
  name: string;
  color: string;
}

export interface Defect {
  id: number;
  defect_number: string;
  title: string;
  description: string;
  status: 'new' | 'in_progress' | 'review' | 'closed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'critical';
  severity: 'cosmetic' | 'minor' | 'major' | 'blocking';
  project: { id: number; name: string };
  category: DefectCategory;
  author: User;
  reporter?: User;
  assignee?: User;
  location: string;
  floor?: string;
  room?: string;
  due_date?: string;
  is_overdue?: boolean;
  days_remaining?: number;
  main_image?: {
    id: number;
    file_url: string;
    filename: string;
  };
  comments_count: number;
  created_at: string;
  updated_at: string;
}

export interface Comment {
  id: number;
  defect_id: number;
  author: User;
  content: string;
  created_at: string;
  updated_at: string;
  is_internal: boolean;
  attachments?: Array<{
    id: number;
    filename: string;
    url: string;
    type: string;
  }>;
  parent_id?: number;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next?: string;
  previous?: string;
}