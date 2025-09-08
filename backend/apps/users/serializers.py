"""
Сериализаторы для пользователей и аутентификации
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, UserProfile, UserSession
from apps.common.utils import get_client_ip


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор профиля пользователя
    """
    age = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'avatar_url', 'bio', 'birth_date', 'age',
            'department', 'hire_date', 'supervisor',
            'email_notifications', 'sms_notifications',
            'theme', 'language'
        ]
    
    def get_avatar_url(self, obj):
        """Получает URL аватара"""
        if obj.avatar:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.avatar.url)
        return None


class UserSerializer(serializers.ModelSerializer):
    """
    Основной сериализатор пользователя
    """
    full_name = serializers.ReadOnlyField(source='get_full_name')
    short_name = serializers.ReadOnlyField(source='get_short_name')
    initials = serializers.ReadOnlyField(source='get_initials')
    role_display = serializers.ReadOnlyField(source='get_role_display_ru')
    profile = UserProfileSerializer(read_only=True)
    is_locked = serializers.ReadOnlyField()
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'middle_name',
            'full_name', 'short_name', 'initials', 'phone', 'position',
            'role', 'role_display', 'is_active', 'is_staff', 'is_locked',
            'is_email_verified', 'must_change_password',
            'last_login', 'date_joined', 'created_at', 'updated_at',
            'profile', 'password'
        ]
        read_only_fields = [
            'id', 'username', 'last_login', 'date_joined', 
            'created_at', 'updated_at', 'is_locked'
        ]
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_password(self, value):
        """Валидация пароля"""
        if value:
            try:
                validate_password(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.messages)
        return value
    
    def validate_email(self, value):
        """Валидация email на уникальность"""
        if self.instance:
            # При обновлении исключаем текущего пользователя
            if User.objects.filter(email=value).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Пользователь с таким email уже существует.")
        else:
            # При создании проверяем уникальность
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError("Пользователь с таким email уже существует.")
        return value
    
    def create(self, validated_data):
        """Создание нового пользователя"""
        password = validated_data.pop('password', None)
        
        # Генерируем username из email если не указан
        if not validated_data.get('username'):
            validated_data['username'] = validated_data['email'].split('@')[0]
        
        user = User.objects.create_user(**validated_data)
        
        if password:
            user.set_password(password)
            user.save()
        
        return user
    
    def update(self, instance, validated_data):
        """Обновление пользователя"""
        password = validated_data.pop('password', None)
        
        # Обновляем поля
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Обновляем пароль если указан
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания пользователя администратором
    """
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = [
            'email', 'first_name', 'last_name', 'middle_name',
            'phone', 'position', 'role', 'is_active',
            'password', 'confirm_password'
        ]
    
    def validate(self, attrs):
        """Валидация паролей"""
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise serializers.ValidationError("Пароли не совпадают.")
        
        return attrs
    
    def validate_password(self, value):
        """Валидация пароля"""
        if value:
            try:
                validate_password(value)
            except ValidationError as e:
                raise serializers.ValidationError(e.messages)
        return value
    
    def create(self, validated_data):
        """Создание пользователя"""
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        # Генерируем username из email
        validated_data['username'] = validated_data['email'].split('@')[0]
        
        user = User.objects.create_user(**validated_data)
        
        if password:
            user.set_password(password)
        else:
            # Генерируем временный пароль
            import secrets
            import string
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
            user.set_password(temp_password)
        
        user.save()
        return user


class UserListSerializer(serializers.ModelSerializer):
    """
    Упрощённый сериализатор для списка пользователей
    """
    full_name = serializers.ReadOnlyField(source='get_full_name')
    role_display = serializers.ReadOnlyField(source='get_role_display_ru')
    
    class Meta:
        model = User
        fields = [
            'id', 'full_name', 'email', 'role', 'role_display',
            'position', 'is_active', 'last_login'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate_old_password(self, value):
        """Проверка старого пароля"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль.")
        return value
    
    def validate(self, attrs):
        """Валидация новых паролей"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Новые пароли не совпадают.")
        
        # Валидация сложности пароля
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError(f"Новый пароль: {'; '.join(e.messages)}")
        
        return attrs
    
    def save(self):
        """Сохранение нового пароля"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Кастомный сериализатор для получения JWT токенов
    """
    
    def validate(self, attrs):
        """Валидация и аутентификация"""
        email = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError('Email и пароль обязательны.')
        
        # Находим пользователя по email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверные учётные данные.')
        
        # Проверяем блокировку аккаунта
        if user.is_locked:
            raise serializers.ValidationError('Аккаунт временно заблокирован. Попробуйте позже.')
        
        # Проверяем активность аккаунта
        if not user.is_active:
            raise serializers.ValidationError('Аккаунт деактивирован.')
        
        # Аутентификация
        user = authenticate(username=user.username, password=password)
        if not user:
            # Увеличиваем счётчик неудачных попыток
            try:
                failed_user = User.objects.get(email=email)
                failed_user.increment_failed_login()
            except User.DoesNotExist:
                pass
            
            raise serializers.ValidationError('Неверные учётные данные.')
        
        # Сбрасываем счётчик неудачных попыток
        user.reset_failed_login()
        
        # Обновляем IP последнего входа
        request = self.context.get('request')
        if request:
            user.last_login_ip = get_client_ip(request)
            user.save(update_fields=['last_login_ip'])
        
        # Получаем токены
        refresh = self.get_token(user)
        
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user, context=self.context).data
        }
    
    @classmethod
    def get_token(cls, user):
        """Получение токена с дополнительными claims"""
        token = super().get_token(user)
        
        # Добавляем дополнительную информацию в токен
        token['user_id'] = user.id
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        
        return token


class UserSessionSerializer(serializers.ModelSerializer):
    """
    Сериализатор сессий пользователя
    """
    browser_info = serializers.ReadOnlyField(source='get_browser_info')
    duration = serializers.ReadOnlyField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'session_key', 'ip_address', 'browser_info',
            'created_at', 'last_activity', 'duration', 'is_active'
        ]
        read_only_fields = ['id', 'session_key', 'created_at']


class PasswordResetSerializer(serializers.Serializer):
    """
    Сериализатор для сброса пароля
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Проверка существования пользователя"""
        try:
            User.objects.get(email=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Сериализатор для подтверждения сброса пароля
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Валидация паролей"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Пароли не совпадают.")
        
        try:
            validate_password(attrs['new_password'])
        except ValidationError as e:
            raise serializers.ValidationError(f"Пароль: {'; '.join(e.messages)}")
        
        return attrs
