/**
 * Компонент для разграничения прав доступа по ролям пользователей
 */

import React from 'react';
import { useAppSelector } from '../../store/index';
import { selectUser } from '../../store/slices/authSlice';

export type UserRole = 'manager' | 'engineer' | 'observer';

export interface Permission {
  roles: UserRole[];
  fallback?: React.ReactNode;
}

interface RoleGuardProps {
  permission: Permission;
  children: React.ReactNode;
}

export const RoleGuard: React.FC<RoleGuardProps> = ({ permission, children }) => {
  const user = useAppSelector(selectUser);

  if (!user) {
    return <>{permission.fallback || null}</>;
  }

  const hasPermission = permission.roles.includes(user.role);

  return <>{hasPermission ? children : (permission.fallback || null)}</>;
};

// Hook для проверки прав доступа
export const usePermissions = () => {
  const user = useAppSelector(selectUser);

  const hasRole = (roles: UserRole[]) => {
    if (!user) return false;
    return roles.includes(user.role);
  };

  const isManager = () => hasRole(['manager']);
  const isEngineer = () => hasRole(['engineer']);
  const isObserver = () => hasRole(['observer']);
  const canEdit = () => hasRole(['manager', 'engineer']);
  const canCreate = () => hasRole(['manager', 'engineer']);
  const canDelete = () => hasRole(['manager']);
  const canAssign = () => hasRole(['manager']);
  const canChangeStatus = () => hasRole(['manager', 'engineer']);
  const canViewReports = () => hasRole(['manager', 'engineer', 'observer']);
  const canManageUsers = () => hasRole(['manager']);
  const canManageProjects = () => hasRole(['manager']);

  return {
    user,
    hasRole,
    isManager,
    isEngineer,
    isObserver,
    canEdit,
    canCreate,
    canDelete,
    canAssign,
    canChangeStatus,
    canViewReports,
    canManageUsers,
    canManageProjects,
  };
};

// Предопределенные разрешения
export const PERMISSIONS = {
  CREATE_DEFECT: { roles: ['manager', 'engineer'] as UserRole[] },
  EDIT_DEFECT: { roles: ['manager', 'engineer'] as UserRole[] },
  DELETE_DEFECT: { roles: ['manager'] as UserRole[] },
  ASSIGN_DEFECT: { roles: ['manager'] as UserRole[] },
  CHANGE_STATUS: { roles: ['manager', 'engineer'] as UserRole[] },
  VIEW_REPORTS: { roles: ['manager', 'engineer', 'observer'] as UserRole[] },
  MANAGE_USERS: { roles: ['manager'] as UserRole[] },
  MANAGE_PROJECTS: { roles: ['manager'] as UserRole[] },
  VIEW_ALL_DEFECTS: { roles: ['manager', 'engineer', 'observer'] as UserRole[] },
  EDIT_COMMENTS: { roles: ['manager', 'engineer'] as UserRole[] },
} as const;

export default RoleGuard;