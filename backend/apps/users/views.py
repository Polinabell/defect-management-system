"""
Views для пользователей и аутентификации
"""

from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout, authenticate
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import User, UserProfile, UserSession
from .serializers import (
    UserSerializer, UserCreateSerializer, UserListSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer,
    UserSessionSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, UserProfileSerializer
)
from apps.common.permissions import CanManageUsers, IsOwnerOrReadOnly
from apps.common.utils import get_client_ip


class CustomTokenObtainPairView(APIView):
    """
    Кастомный view для получения JWT токенов
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        """Логин пользователя"""
        try:
            username_or_email = request.data.get('email') or request.data.get('username')
            password = request.data.get('password')
            
            if not username_or_email or not password:
                return Response(
                    {'error': 'Email/Username и пароль обязательны.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Находим пользователя
            try:
                if '@' in username_or_email:
                    user = User.objects.get(email=username_or_email)
                else:
                    user = User.objects.get(username=username_or_email)
            except User.DoesNotExist:
                return Response(
                    {'error': 'Неверные учётные данные.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Аутентификация
            user = authenticate(username=user.username, password=password)
            if not user:
                return Response(
                    {'error': 'Неверные учётные данные.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Создаём токены
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': 'Ошибка аутентификации', 'details': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """
    View для выхода из системы
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Выход из системы с blacklist токена"""
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            # Деактивируем сессию
            session_key = request.session.session_key
            if session_key:
                UserSession.objects.filter(
                    user=request.user,
                    session_key=session_key
                ).update(is_active=False)
            
            logout(request)
            
            return Response(
                {"message": "Успешный выход из системы"},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": "Ошибка при выходе из системы"},
                status=status.HTTP_400_BAD_REQUEST
            )


class RegisterView(generics.CreateAPIView):
    """
    View для регистрации новых пользователей
    """
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        """Создание пользователя с дополнительной логикой"""
        user = serializer.save()
        
        # Создаём профиль пользователя
        UserProfile.objects.get_or_create(user=user)
        
        return user
    
    def create(self, request, *args, **kwargs):
        """Переопределяем create для возврата токенов"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = self.perform_create(serializer)
        
        # Генерируем токены для нового пользователя
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)


class UserListCreateView(generics.ListCreateAPIView):
    """
    Список пользователей и создание нового пользователя
    """
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['first_name', 'last_name', 'email', 'position']
    filterset_fields = ['role', 'is_active', 'is_staff']
    ordering_fields = ['last_name', 'first_name', 'email', 'date_joined', 'last_login']
    ordering = ['last_name', 'first_name']
    
    def get_serializer_class(self):
        """Выбор сериализатора в зависимости от действия"""
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer
    
    def get_permissions(self):
        """Права доступа"""
        if self.request.method == 'POST':
            self.permission_classes = [CanManageUsers]
        return super().get_permissions()
    
    def get_queryset(self):
        """Фильтрация пользователей по роли текущего пользователя"""
        queryset = super().get_queryset()
        
        # Администраторы видят всех
        if self.request.user.is_admin:
            return queryset
        
        # Менеджеры видят инженеров и наблюдателей
        if self.request.user.is_manager:
            return queryset.filter(
                role__in=[User.Role.ENGINEER, User.Role.OBSERVER, User.Role.MANAGER]
            )
        
        # Инженеры и наблюдатели видят только себя и других инженеров
        return queryset.filter(
            Q(role__in=[User.Role.ENGINEER, User.Role.OBSERVER]) |
            Q(id=self.request.user.id)
        )


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Детали, обновление и удаление пользователя
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Права доступа"""
        if self.request.method in ['PUT', 'PATCH']:
            # Пользователь может редактировать только себя, админы - всех
            if self.get_object().id == self.request.user.id:
                self.permission_classes = [permissions.IsAuthenticated]
            else:
                self.permission_classes = [CanManageUsers]
        elif self.request.method == 'DELETE':
            self.permission_classes = [CanManageUsers]
        
        return super().get_permissions()
    
    def get_queryset(self):
        """Фильтрация доступных пользователей"""
        if self.request.user.is_admin:
            return super().get_queryset()
        
        # Обычные пользователи могут видеть только себя
        return super().get_queryset().filter(id=self.request.user.id)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    Профиль текущего пользователя
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Возвращает текущего пользователя"""
        return self.request.user


class ChangePasswordView(APIView):
    """
    Смена пароля пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Смена пароля"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Пароль успешно изменён"},
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    Профиль пользователя
    """
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_object(self):
        """Получает или создаёт профиль пользователя"""
        profile, created = UserProfile.objects.get_or_create(
            user=self.request.user
        )
        return profile


class UserSessionsView(generics.ListAPIView):
    """
    Список активных сессий пользователя
    """
    serializer_class = UserSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Возвращает сессии текущего пользователя"""
        return UserSession.objects.filter(
            user=self.request.user,
            is_active=True
        ).order_by('-last_activity')


class TerminateSessionView(APIView):
    """
    Завершение сессии пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, session_id):
        """Завершение указанной сессии"""
        try:
            session = UserSession.objects.get(
                id=session_id,
                user=request.user,
                is_active=True
            )
            session.is_active = False
            session.save()
            
            return Response(
                {"message": "Сессия завершена"},
                status=status.HTTP_200_OK
            )
        except UserSession.DoesNotExist:
            return Response(
                {"error": "Сессия не найдена"},
                status=status.HTTP_404_NOT_FOUND
            )


class PasswordResetView(APIView):
    """
    Запрос на сброс пароля
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Отправка email для сброса пароля"""
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            # TODO: Реализовать отправку email с токеном сброса
            # В реальном проекте здесь будет отправка email
            
            return Response(
                {"message": "Инструкции по сбросу пароля отправлены на email"},
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordResetConfirmView(APIView):
    """
    Подтверждение сброса пароля
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Установка нового пароля по токену"""
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            # TODO: Реализовать проверку токена и установку пароля
            # В реальном проекте здесь будет проверка токена из email
            
            return Response(
                {"message": "Пароль успешно изменён"},
                status=status.HTTP_200_OK
            )
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_stats(request):
    """
    Статистика пользователей (только для администраторов)
    """
    if not request.user.is_admin:
        return Response(
            {"error": "Недостаточно прав"},
            status=status.HTTP_403_FORBIDDEN
        )
    
    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'users_by_role': {
            role[0]: User.objects.filter(role=role[0]).count()
            for role in User.Role.choices
        },
        'locked_users': User.objects.filter(locked_until__isnull=False).count(),
        'must_change_password': User.objects.filter(must_change_password=True).count(),
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([CanManageUsers])
def unlock_user(request, user_id):
    """
    Разблокировка пользователя администратором
    """
    try:
        user = User.objects.get(id=user_id)
        user.unlock_account()
        
        return Response(
            {"message": f"Пользователь {user.get_full_name()} разблокирован"},
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {"error": "Пользователь не найден"},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([CanManageUsers])
def reset_user_password(request, user_id):
    """
    Сброс пароля пользователя администратором
    """
    try:
        user = User.objects.get(id=user_id)
        
        # Генерируем новый временный пароль
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
        
        user.set_password(temp_password)
        user.must_change_password = True
        user.save()
        
        # TODO: Отправить новый пароль пользователю по email
        
        return Response(
            {"message": f"Пароль пользователя {user.get_full_name()} сброшен"},
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {"error": "Пользователь не найден"},
            status=status.HTTP_404_NOT_FOUND
        )
