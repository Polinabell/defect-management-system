"""
Тесты для приложения users
"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, UserSession

User = get_user_model()


class UserModelTest(TestCase):
    """
    Тесты модели User
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'first_name': 'Иван',
            'last_name': 'Иванов',
            'middle_name': 'Иванович',
            'role': User.Role.ENGINEER,
            'position': 'Инженер-строитель'
        }
    
    def test_create_user(self):
        """Тест создания пользователя"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.role, User.Role.ENGINEER)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.must_change_password)
    
    def test_get_full_name(self):
        """Тест получения полного имени"""
        user = User.objects.create_user(**self.user_data)
        expected_name = 'Иванов Иван Иванович'
        self.assertEqual(user.get_full_name(), expected_name)
    
    def test_get_short_name(self):
        """Тест получения краткого имени"""
        user = User.objects.create_user(**self.user_data)
        expected_name = 'Иван Иванов'
        self.assertEqual(user.get_short_name(), expected_name)
    
    def test_get_initials(self):
        """Тест получения инициалов"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_initials(), 'ИИ')
    
    def test_role_properties(self):
        """Тест проверки ролей"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertTrue(user.is_engineer)
        self.assertFalse(user.is_manager)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_observer)
    
    def test_account_locking(self):
        """Тест блокировки аккаунта"""
        user = User.objects.create_user(**self.user_data)
        
        # Изначально аккаунт не заблокирован
        self.assertFalse(user.is_locked)
        
        # Блокируем аккаунт
        user.lock_account()
        self.assertTrue(user.is_locked)
        
        # Разблокируем аккаунт
        user.unlock_account()
        self.assertFalse(user.is_locked)
    
    def test_failed_login_increment(self):
        """Тест увеличения счётчика неудачных попыток"""
        user = User.objects.create_user(**self.user_data)
        
        # Изначально 0 неудачных попыток
        self.assertEqual(user.failed_login_attempts, 0)
        
        # Увеличиваем счётчик
        for i in range(1, 6):
            user.increment_failed_login()
            if i < 5:
                self.assertEqual(user.failed_login_attempts, i)
                self.assertFalse(user.is_locked)
            else:
                # После 5 попыток аккаунт блокируется
                self.assertEqual(user.failed_login_attempts, 5)
                self.assertTrue(user.is_locked)
    
    def test_password_change_tracking(self):
        """Тест отслеживания смены пароля"""
        user = User.objects.create_user(**self.user_data)
        
        # Изначально требуется смена пароля
        self.assertTrue(user.must_change_password)
        self.assertIsNone(user.password_changed_at)
        
        # Меняем пароль
        user.set_password('new_password123')
        
        self.assertFalse(user.must_change_password)
        self.assertIsNotNone(user.password_changed_at)


class UserProfileTest(TestCase):
    """
    Тесты модели UserProfile
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Иван',
            last_name='Иванов'
        )
    
    def test_profile_creation(self):
        """Тест создания профиля"""
        # Профиль должен создаваться автоматически
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
    
    def test_age_calculation(self):
        """Тест вычисления возраста"""
        from datetime import date
        
        # Устанавливаем дату рождения
        birth_date = date(1990, 5, 15)
        self.user.profile.birth_date = birth_date
        self.user.profile.save()
        
        # Проверяем, что возраст вычисляется
        age = self.user.profile.age
        self.assertIsInstance(age, int)
        self.assertGreater(age, 0)


class AuthenticationAPITest(APITestCase):
    """
    Тесты API аутентификации
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Иван',
            last_name='Иванов',
            role=User.Role.ENGINEER
        )
        self.user.set_password('testpass123')
        self.user.save()
        
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.change_password_url = reverse('users:change-password')
    
    def test_login_success(self):
        """Тест успешного входа"""
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_login_invalid_credentials(self):
        """Тест входа с неверными данными"""
        data = {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Проверяем, что счётчик неудачных попыток увеличился
        self.user.refresh_from_db()
        self.assertEqual(self.user.failed_login_attempts, 1)
    
    def test_login_locked_account(self):
        """Тест входа с заблокированным аккаунтом"""
        # Блокируем аккаунт
        self.user.lock_account()
        
        data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('заблокирован', str(response.data))
    
    def test_logout(self):
        """Тест выхода из системы"""
        # Получаем токен
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Авторизуемся
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Выходим из системы
        data = {'refresh_token': str(refresh)}
        response = self.client.post(self.logout_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_change_password(self):
        """Тест смены пароля"""
        # Авторизуемся
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        data = {
            'old_password': 'testpass123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }
        
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что пароль действительно изменился
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword456'))


class UserAPITest(APITestCase):
    """
    Тесты API пользователей
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        # Создаём администратора
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            first_name='Админ',
            last_name='Админов',
            role=User.Role.ADMIN,
            is_staff=True
        )
        
        # Создаём обычного пользователя
        self.user = User.objects.create_user(
            email='user@example.com',
            username='user',
            first_name='Пользователь',
            last_name='Пользователев',
            role=User.Role.ENGINEER
        )
        
        self.users_url = reverse('users:user-list-create')
        self.current_user_url = reverse('users:current-user')
    
    def test_list_users_as_admin(self):
        """Тест получения списка пользователей администратором"""
        # Авторизуемся как администратор
        refresh = RefreshToken.for_user(self.admin)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get(self.users_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # admin + user
    
    def test_create_user_as_admin(self):
        """Тест создания пользователя администратором"""
        # Авторизуемся как администратор
        refresh = RefreshToken.for_user(self.admin)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'role': User.Role.ENGINEER,
            'password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }
        
        response = self.client.post(self.users_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_get_current_user(self):
        """Тест получения текущего пользователя"""
        # Авторизуемся
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        response = self.client.get(self.current_user_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user.email)
    
    def test_update_current_user(self):
        """Тест обновления текущего пользователя"""
        # Авторизуемся
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        data = {
            'first_name': 'Обновлённое',
            'last_name': 'Имя',
            'position': 'Старший инженер'
        }
        
        response = self.client.patch(self.current_user_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Обновлённое')
        self.assertEqual(self.user.position, 'Старший инженер')


class UserSessionTest(TestCase):
    """
    Тесты модели UserSession
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            first_name='Тест',
            last_name='Пользователь'
        )
    
    def test_create_session(self):
        """Тест создания сессии"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        
        self.assertEqual(session.user, self.user)
        self.assertTrue(session.is_active)
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.last_activity)
    
    def test_browser_info_parsing(self):
        """Тест парсинга информации о браузере"""
        session = UserSession.objects.create(
            user=self.user,
            session_key='test_session_key',
            ip_address='127.0.0.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        
        browser_info = session.get_browser_info()
        self.assertIn('Chrome', browser_info)
        self.assertIn('Windows', browser_info)


class PermissionsTest(APITestCase):
    """
    Тесты прав доступа
    """
    
    def setUp(self):
        """Подготовка данных для тестов"""
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            role=User.Role.ADMIN,
            is_staff=True
        )
        
        self.manager = User.objects.create_user(
            email='manager@example.com',
            username='manager',
            role=User.Role.MANAGER
        )
        
        self.engineer = User.objects.create_user(
            email='engineer@example.com',
            username='engineer',
            role=User.Role.ENGINEER
        )
        
        self.observer = User.objects.create_user(
            email='observer@example.com',
            username='observer',
            role=User.Role.OBSERVER
        )
    
    def _authenticate(self, user):
        """Хелпер для аутентификации пользователя"""
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    def test_admin_can_create_users(self):
        """Тест: администратор может создавать пользователей"""
        self._authenticate(self.admin)
        
        data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'role': User.Role.ENGINEER
        }
        
        response = self.client.post(reverse('users:user-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_engineer_cannot_create_users(self):
        """Тест: инженер не может создавать пользователей"""
        self._authenticate(self.engineer)
        
        data = {
            'email': 'newuser@example.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'role': User.Role.ENGINEER
        }
        
        response = self.client.post(reverse('users:user-list-create'), data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_can_edit_own_profile(self):
        """Тест: пользователь может редактировать свой профиль"""
        self._authenticate(self.engineer)
        
        data = {'first_name': 'Новое имя'}
        response = self.client.patch(reverse('users:current-user'), data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_user_cannot_edit_other_users(self):
        """Тест: пользователь не может редактировать других пользователей"""
        self._authenticate(self.engineer)
        
        data = {'first_name': 'Новое имя'}
        response = self.client.patch(
            reverse('users:user-detail', args=[self.manager.id]),
            data
        )
        
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND])
