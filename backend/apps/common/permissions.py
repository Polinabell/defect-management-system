"""
Упрощенные права доступа для демо версии
"""

from rest_framework import permissions
from rest_framework.permissions import BasePermission


class IsOwnerOrReadOnly(BasePermission):
    """
    Право доступа: владелец может изменять, остальные только читать
    """
    
    def has_object_permission(self, request, view, obj):
        # Права на чтение для всех аутентифицированных
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Права на запись только для владельца или администратора
        return (
            hasattr(obj, 'created_by') and obj.created_by == request.user or
            hasattr(obj, 'author') and obj.author == request.user or
            request.user.is_staff
        )


class CanManageUsers(BasePermission):
    """
    Право доступа: может управлять пользователями
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return (
            request.user.is_staff or 
            getattr(request.user, 'role', '') == 'manager'
        )


class IsProjectMember(BasePermission):
    """
    Право доступа: пользователь является участником проекта
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Получаем проект из объекта
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, 'defect'):
            project = obj.defect.project
        else:
            project = obj
        
        # Простая проверка - менеджер проекта или участник
        return (
            hasattr(project, 'manager') and project.manager == request.user or
            hasattr(project, 'members') and project.members.filter(user=request.user).exists()
        )


class IsProjectManagerOrReadOnly(BasePermission):
    """
    Право доступа: менеджер проекта может изменять, остальные только читать
    """
    
    def has_object_permission(self, request, view, obj):
        # Права на чтение для всех участников проекта
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Права на запись только для менеджера проекта или администратора
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
            
        return (
            hasattr(project, 'manager') and project.manager == request.user or
            request.user.is_staff
        )


class CanAssignDefects(BasePermission):
    """
    Право доступа: может назначать дефекты
    """
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (request.user.is_staff or getattr(request.user, 'role', '') == 'manager')
        )


class CanChangeDefectStatus(BasePermission):
    """
    Право доступа: может изменять статус дефекта
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Администраторы могут всё
        if request.user.is_staff:
            return True
        
        # Менеджеры могут изменять любые статусы
        if getattr(request.user, 'role', '') == 'manager':
            return True
        
        # Исполнители могут изменять статусы назначенных им дефектов
        if hasattr(obj, 'assignee') and obj.assignee == request.user:
            return True
        
        return False


class IsDefectAssigneeOrAuthor(BasePermission):
    """
    Право доступа: исполнитель или автор дефекта
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # Администраторы могут всё
        if request.user.is_staff:
            return True
        
        # Автор дефекта может изменять
        if hasattr(obj, 'author') and obj.author == request.user:
            return True
        
        # Исполнитель дефекта может изменять
        if hasattr(obj, 'assignee') and obj.assignee == request.user:
            return True
        
        return False