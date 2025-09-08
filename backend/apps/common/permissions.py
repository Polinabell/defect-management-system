"""
Общие permissions для всех приложений
"""

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.views import APIView
from typing import Any


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Разрешение только владельцу объекта редактировать его,
    остальным только чтение
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        # Права на чтение разрешены для любого запроса,
        # поэтому мы всегда разрешаем GET, HEAD или OPTIONS запросы.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Права на запись только для владельца объекта.
        return hasattr(obj, 'owner') and obj.owner == request.user


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение только автору объекта редактировать его,
    остальным только чтение
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        # Права на чтение разрешены для любого запроса
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Права на запись только для автора объекта
        return hasattr(obj, 'author') and obj.author == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешение только администраторам редактировать,
    остальным только чтение
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return request.user.is_authenticated and request.user.is_staff


class IsManagerOrReadOnly(permissions.BasePermission):
    """
    Разрешение менеджерам и администраторам редактировать,
    остальным только чтение
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        
        return (
            request.user.is_authenticated and 
            hasattr(request.user, 'role') and
            request.user.role in ['admin', 'manager']
        )


class IsProjectMember(permissions.BasePermission):
    """
    Разрешение только участникам проекта
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if not request.user.is_authenticated:
            return False
        
        # Если у объекта есть поле project
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
            project = obj
        else:
            return False
        
        # Проверяем участие в проекте
        return project.members.filter(id=request.user.id).exists()


class IsProjectManagerOrReadOnly(permissions.BasePermission):
    """
    Разрешение менеджеру проекта редактировать,
    участникам только чтение
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if not request.user.is_authenticated:
            return False
        
        # Получаем проект
        if hasattr(obj, 'project'):
            project = obj.project
        elif hasattr(obj, '__class__') and obj.__class__.__name__ == 'Project':
            project = obj
        else:
            return False
        
        # Проверяем участие в проекте
        if not project.members.filter(id=request.user.id).exists():
            return False
        
        # Если запрос на чтение, разрешаем участникам
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Если запрос на изменение, проверяем роль
        return (
            project.manager == request.user or
            request.user.role in ['admin', 'manager']
        )


class CanAssignDefects(permissions.BasePermission):
    """
    Разрешение назначать дефекты только менеджерам
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user.is_authenticated:
            return False
        
        return (
            hasattr(request.user, 'role') and
            request.user.role in ['admin', 'manager']
        )


class CanManageUsers(permissions.BasePermission):
    """
    Разрешение управлять пользователями только администраторам
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        return (
            request.user.is_authenticated and
            request.user.is_staff and
            hasattr(request.user, 'role') and
            request.user.role == 'admin'
        )


class IsDefectAssigneeOrAuthor(permissions.BasePermission):
    """
    Разрешение автору или исполнителю дефекта
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if not request.user.is_authenticated:
            return False
        
        return (
            obj.author == request.user or
            obj.assignee == request.user or
            (hasattr(obj, 'project') and obj.project.manager == request.user) or
            request.user.role in ['admin', 'manager']
        )


class CanChangeDefectStatus(permissions.BasePermission):
    """
    Разрешение изменять статус дефекта
    """
    
    def has_object_permission(self, request: Request, view: APIView, obj: Any) -> bool:
        if not request.user.is_authenticated:
            return False
        
        # Автор может изменить статус с "новый" на "отменён"
        if obj.author == request.user:
            return True
        
        # Исполнитель может изменить статус с "в работе" на "на проверке"
        if obj.assignee == request.user:
            return True
        
        # Менеджер проекта может изменить любой статус
        if hasattr(obj, 'project') and obj.project.manager == request.user:
            return True
        
        # Администраторы и менеджеры могут изменить любой статус
        return request.user.role in ['admin', 'manager']


class ReadOnlyPermission(permissions.BasePermission):
    """
    Разрешение только на чтение
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.method in permissions.SAFE_METHODS and request.user.is_authenticated


class DynamicPermission(permissions.BasePermission):
    """
    Динамическое разрешение на основе роли пользователя
    """
    
    def has_permission(self, request: Request, view: APIView) -> bool:
        if not request.user.is_authenticated:
            return False
        
        # Получаем роль пользователя
        user_role = getattr(request.user, 'role', 'observer')
        
        # Определяем разрешения по ролям
        role_permissions = {
            'admin': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
            'manager': ['GET', 'POST', 'PUT', 'PATCH'],
            'engineer': ['GET', 'POST', 'PUT', 'PATCH'],
            'observer': ['GET'],
        }
        
        allowed_methods = role_permissions.get(user_role, ['GET'])
        return request.method in allowed_methods
