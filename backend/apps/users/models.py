"""
Модели пользователей и профилей
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField
from apps.common.models import BaseModel


class User(AbstractUser):
    """
    Кастомная модель пользователя с ролями
    """
    
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Администратор'
        MANAGER = 'manager', 'Менеджер проекта'
        ENGINEER = 'engineer', 'Инженер'
        OBSERVER = 'observer', 'Наблюдатель'
    
    # Основная информация
    email = models.EmailField(
        verbose_name='Email',
        unique=True,
        help_text='Уникальный email адрес пользователя'
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=20,
        choices=Role.choices,
        default=Role.ENGINEER,
        help_text='Роль пользователя в системе'
    )
    
    # Личная информация
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text='Имя пользователя'
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        help_text='Фамилия пользователя'
    )
    middle_name = models.CharField(
        verbose_name='Отчество',
        max_length=150,
        blank=True,
        help_text='Отчество пользователя (опционально)'
    )
    
    # Контактная информация
    phone = PhoneNumberField(
        verbose_name='Телефон',
        blank=True,
        help_text='Номер телефона пользователя'
    )
    position = models.CharField(
        verbose_name='Должность',
        max_length=200,
        blank=True,
        help_text='Должность на предприятии'
    )
    
    # Настройки аккаунта
    is_email_verified = models.BooleanField(
        verbose_name='Email подтверждён',
        default=False,
        help_text='Подтверждён ли email адрес'
    )
    must_change_password = models.BooleanField(
        verbose_name='Необходимо сменить пароль',
        default=True,
        help_text='Требуется ли смена пароля при следующем входе'
    )
    password_changed_at = models.DateTimeField(
        verbose_name='Дата смены пароля',
        null=True,
        blank=True,
        help_text='Дата последней смены пароля'
    )
    
    # Активность
    last_login_ip = models.GenericIPAddressField(
        verbose_name='IP последнего входа',
        null=True,
        blank=True,
        help_text='IP адрес последнего входа в систему'
    )
    failed_login_attempts = models.PositiveIntegerField(
        verbose_name='Неудачные попытки входа',
        default=0,
        help_text='Количество неудачных попыток входа подряд'
    )
    locked_until = models.DateTimeField(
        verbose_name='Заблокирован до',
        null=True,
        blank=True,
        help_text='Время до которого аккаунт заблокирован'
    )
    
    # Метаданные
    created_at = models.DateTimeField(
        verbose_name='Дата создания',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата обновления',
        auto_now=True
    )
    
    # Используем email для входа вместо username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.get_full_name() or self.email
    
    def get_full_name(self):
        """
        Возвращает полное имя пользователя
        """
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}".strip()
    
    def get_short_name(self):
        """
        Возвращает краткое имя пользователя
        """
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_initials(self):
        """
        Возвращает инициалы пользователя
        """
        initials = []
        if self.first_name:
            initials.append(self.first_name[0].upper())
        if self.last_name:
            initials.append(self.last_name[0].upper())
        return ''.join(initials)
    
    @property
    def is_admin(self):
        """Проверка роли администратора"""
        return self.role == self.Role.ADMIN
    
    @property
    def is_manager(self):
        """Проверка роли менеджера"""
        return self.role == self.Role.MANAGER
    
    @property
    def is_engineer(self):
        """Проверка роли инженера"""
        return self.role == self.Role.ENGINEER
    
    @property
    def is_observer(self):
        """Проверка роли наблюдателя"""
        return self.role == self.Role.OBSERVER
    
    @property
    def is_locked(self):
        """Проверка блокировки аккаунта"""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def lock_account(self, duration_minutes=15):
        """
        Блокирует аккаунт на указанное время
        """
        self.locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['locked_until'])
    
    def unlock_account(self):
        """
        Разблокирует аккаунт
        """
        self.locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['locked_until', 'failed_login_attempts'])
    
    def increment_failed_login(self):
        """
        Увеличивает счётчик неудачных попыток входа
        """
        self.failed_login_attempts += 1
        
        # Блокируем после 5 неудачных попыток
        if self.failed_login_attempts >= 5:
            self.lock_account()
        
        self.save(update_fields=['failed_login_attempts'])
    
    def reset_failed_login(self):
        """
        Сбрасывает счётчик неудачных попыток входа
        """
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])
    
    def set_password(self, raw_password):
        """
        Переопределяем метод установки пароля для отслеживания изменений
        """
        super().set_password(raw_password)
        self.password_changed_at = timezone.now()
        self.must_change_password = False
    
    def get_role_display_ru(self):
        """
        Возвращает русское название роли
        """
        return dict(self.Role.choices).get(self.role, self.role)


class UserProfile(BaseModel):
    """
    Дополнительная информация профиля пользователя
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь'
    )
    
    # Дополнительная информация
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars/%Y/%m/',
        blank=True,
        help_text='Фотография пользователя'
    )
    bio = models.TextField(
        verbose_name='О себе',
        blank=True,
        max_length=500,
        help_text='Краткая информация о пользователе'
    )
    birth_date = models.DateField(
        verbose_name='Дата рождения',
        null=True,
        blank=True
    )
    
    # Рабочая информация
    department = models.CharField(
        verbose_name='Отдел',
        max_length=200,
        blank=True,
        help_text='Отдел/подразделение'
    )
    hire_date = models.DateField(
        verbose_name='Дата приёма на работу',
        null=True,
        blank=True
    )
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name='Руководитель'
    )
    
    # Настройки уведомлений
    email_notifications = models.BooleanField(
        verbose_name='Email уведомления',
        default=True,
        help_text='Получать уведомления по email'
    )
    sms_notifications = models.BooleanField(
        verbose_name='SMS уведомления',
        default=False,
        help_text='Получать уведомления по SMS'
    )
    
    # Настройки интерфейса
    theme = models.CharField(
        verbose_name='Тема интерфейса',
        max_length=20,
        choices=[
            ('light', 'Светлая'),
            ('dark', 'Тёмная'),
            ('auto', 'Автоматическая'),
        ],
        default='light'
    )
    language = models.CharField(
        verbose_name='Язык интерфейса',
        max_length=10,
        choices=[
            ('ru', 'Русский'),
            ('en', 'English'),
        ],
        default='ru'
    )
    
    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'
    
    def __str__(self):
        return f"Профиль {self.user.get_full_name()}"
    
    @property
    def age(self):
        """Вычисляет возраст пользователя"""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class UserSession(models.Model):
    """
    Модель для отслеживания сессий пользователей
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions',
        verbose_name='Пользователь'
    )
    session_key = models.CharField(
        verbose_name='Ключ сессии',
        max_length=40,
        unique=True
    )
    ip_address = models.GenericIPAddressField(
        verbose_name='IP адрес',
        help_text='IP адрес пользователя'
    )
    user_agent = models.TextField(
        verbose_name='User Agent',
        help_text='Информация о браузере'
    )
    created_at = models.DateTimeField(
        verbose_name='Начало сессии',
        auto_now_add=True
    )
    last_activity = models.DateTimeField(
        verbose_name='Последняя активность',
        auto_now=True
    )
    is_active = models.BooleanField(
        verbose_name='Активна',
        default=True
    )
    
    class Meta:
        verbose_name = 'Сессия пользователя'
        verbose_name_plural = 'Сессии пользователей'
        ordering = ['-last_activity']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
        ]
    
    def __str__(self):
        return f"Сессия {self.user.email} от {self.created_at.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def duration(self):
        """Продолжительность сессии"""
        return self.last_activity - self.created_at
    
    def get_browser_info(self):
        """Парсит информацию о браузере из User-Agent"""
        # Упрощённый парсер User-Agent
        user_agent = self.user_agent.lower()
        
        if 'chrome' in user_agent:
            browser = 'Chrome'
        elif 'firefox' in user_agent:
            browser = 'Firefox'
        elif 'safari' in user_agent:
            browser = 'Safari'
        elif 'edge' in user_agent:
            browser = 'Edge'
        else:
            browser = 'Неизвестный'
        
        if 'windows' in user_agent:
            os = 'Windows'
        elif 'mac' in user_agent:
            os = 'macOS'
        elif 'linux' in user_agent:
            os = 'Linux'
        elif 'android' in user_agent:
            os = 'Android'
        elif 'iphone' in user_agent or 'ipad' in user_agent:
            os = 'iOS'
        else:
            os = 'Неизвестная'
        
        return f"{browser} на {os}"
