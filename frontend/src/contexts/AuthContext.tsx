/**
 * Контекст аутентификации
 */

import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'manager' | 'engineer' | 'observer';
  is_active: boolean;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  loading: boolean;
  hasPermission: (permission: string) => boolean;
  isManager: boolean;
  isEngineer: boolean;
  isObserver: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Проверяем сохраненный токен и пользователя
    const token = localStorage.getItem('token');
    const savedUser = localStorage.getItem('user');
    
    if (token && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
      } catch (error) {
        console.error('Error parsing saved user:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    setLoading(true);
    try {
      // Имитация API запроса
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Демо пользователи для разных ролей
      const demoUsers = {
        'manager': {
          id: 1,
          username: 'manager',
          email: 'manager@example.com',
          first_name: 'Анна',
          last_name: 'Менеджерова',
          role: 'manager' as const,
          is_active: true,
          created_at: new Date().toISOString()
        },
        'engineer': {
          id: 2,
          username: 'engineer',
          email: 'engineer@example.com',
          first_name: 'Петр',
          last_name: 'Инженеров',
          role: 'engineer' as const,
          is_active: true,
          created_at: new Date().toISOString()
        },
        'observer': {
          id: 3,
          username: 'observer',
          email: 'observer@example.com',
          first_name: 'Мария',
          last_name: 'Наблюдательева',
          role: 'observer' as const,
          is_active: true,
          created_at: new Date().toISOString()
        }
      };

      if (password === 'password' && demoUsers[username as keyof typeof demoUsers]) {
        const user = demoUsers[username as keyof typeof demoUsers];
        setUser(user);
        localStorage.setItem('token', `mock_token_${user.id}`);
        localStorage.setItem('user', JSON.stringify(user));
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login error:', error);
      return false;
    } finally {
      setLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  // Система разграничения прав доступа
  const hasPermission = (permission: string): boolean => {
    if (!user) return false;
    
    const permissions = {
      manager: [
        'create_project', 'update_project', 'delete_project',
        'create_defect', 'update_defect', 'delete_defect', 'assign_defect',
        'view_all_projects', 'view_all_defects', 'view_reports',
        'manage_users', 'export_data'
      ],
      engineer: [
        'view_assigned_projects', 'create_defect', 'update_own_defect',
        'view_assigned_defects', 'comment_defect', 'upload_attachment'
      ],
      observer: [
        'view_assigned_projects', 'view_assigned_defects', 'view_reports'
      ]
    };
    
    return permissions[user.role]?.includes(permission) || false;
  };

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated: !!user,
      login,
      logout,
      loading,
      hasPermission,
      isManager: user?.role === 'manager',
      isEngineer: user?.role === 'engineer',
      isObserver: user?.role === 'observer'
    }}>
      {children}
    </AuthContext.Provider>
  );
};