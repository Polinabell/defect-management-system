"""
Кастомные права доступа для API
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class CanManageUsers(BasePermission):
    """Разрешение на управление пользователями"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_staff or
            getattr(request.user, 'role', 'observer') == 'manager'
        )


class IsOwnerOrReadOnly(BasePermission):
    """Разрешение на редактирование только владельцем"""
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user or request.user.is_staff


class IsProjectMember(BasePermission):
    """
    Право доступа: пользователь является участником проекта
    """
    
    def has_object_permission(self, request, view, obj):
        """Проверка прав на уровне объекта"""
        # Для администраторов
        if request.user.is_staff or getattr(request.user, 'is_admin', False):
            return True
        
        # Получаем проект из объекта
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'defect'):
            project = obj.defect.project
        else:
            project = obj
        
        # Проверяем является ли пользователь участником проекта
        return project.is_member(request.user)


class IsDefectAssigneeOrAuthor(BasePermission):
    """
    Право доступа: пользователь является автором или исполнителем дефекта
    """
    
    def has_object_permission(self, request, view, obj):
        """Проверка прав на уровне объекта"""
        # Для администраторов
        if request.user.is_staff or getattr(request.user, 'is_admin', False):
            return True
        
        # Получаем дефект из объекта
        if hasattr(obj, 'defect'):
            defect = obj.defect
        else:
            defect = obj
        
        # Автор или исполнитель дефекта
        if defect.author == request.user or defect.assignee == request.user:
            return True
        
        # Менеджер проекта
        if defect.project.manager == request.user:
            return True
        
        return False


class CanChangeDefectStatus(BasePermission):
    """
    Право доступа: может изменять статус дефекта
    """
    
    def has_permission(self, request, view):
        """Проверка общих прав"""
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        """Проверка прав на уровне объекта"""
        # Для администраторов
        if request.user.is_staff or getattr(request.user, 'is_admin', False):
            return True
        
        # Получаем дефект
        defect = obj
        
        # Менеджер проекта может изменять любые статусы
        if defect.project.manager == request.user:
            return True
        
        # Исполнитель может изменять определённые статусы
        if defect.assignee == request.user:
            return True
        
        # Автор может изменять только новые дефекты
        if defect.author == request.user and defect.status == 'new':
            return True
        
        return False


class CanAssignDefects(BasePermission):
    """
    Право доступа: может назначать исполнителей дефектов
    """
    
    def has_permission(self, request, view):
        """Проверка общих прав"""
        if not request.user.is_authenticated:
            return False
        
        # Только менеджеры и администраторы могут назначать
        return (
            request.user.is_staff or 
            getattr(request.user, 'is_admin', False) or
            getattr(request.user, 'role', '') == 'manager'
        )


class IsManagerOrAdmin(BasePermission):
    """
    Право доступа: только менеджеры и администраторы
    """
    
    def has_permission(self, request, view):
        """Проверка общих прав"""
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_staff or 
            getattr(request.user, 'is_admin', False) or
            getattr(request.user, 'role', '') == 'manager'
        )


class IsOwnerOrReadOnly(BasePermission):
    """
    Право доступа: владелец может изменять, остальные только читать
    """
    
    def has_object_permission(self, request, view, obj):
        """Проверка прав на уровне объекта"""
        # Права на чтение для всех аутентифицированных
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Права на запись только для владельца или администратора
        return (
            obj.created_by == request.user or
            request.user.is_staff or
            getattr(request.user, 'is_admin', False)
        )