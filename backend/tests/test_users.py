"""
Тесты для модуля пользователей
"""

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from .base import BaseAPITestCase, SecurityTestMixin
from .factories import UserFactory, AdminUserFactory, ManagerUserFactory

User = get_user_model()


class UserModelTest(BaseAPITestCase):
    """Тесты модели пользователя"""
    
    def test_user_creation(self):
        """Тест создания пользователя"""
        user = UserFactory()
        self.assertIsInstance(user, User)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertIn(user.role, ['engineer', 'manager', 'observer'])
    
    def test_admin_user_creation(self):
        """Тест создания администратора"""
        admin = AdminUserFactory()
        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertEqual(admin.role, 'admin')
    
    def test_user_str_representation(self):
        """Тест строкового представления пользователя"""
        user = UserFactory(username='testuser')
        self.assertEqual(str(user), 'testuser')
    
    def test_user_get_full_name(self):
        """Тест получения полного имени"""
        user = UserFactory(first_name='Иван', last_name='Петров')
        self.assertEqual(user.get_full_name(), 'Иван Петров')
    
    def test_user_get_short_name(self):
        """Тест получения короткого имени"""
        user = UserFactory(first_name='Иван')
        self.assertEqual(user.get_short_name(), 'Иван')
    
    def test_user_role_choices(self):
        """Тест выбора ролей пользователя"""
        valid_roles = ['engineer', 'manager', 'observer', 'admin']
        for role in valid_roles:
            user = UserFactory(role=role)
            self.assertEqual(user.role, role)
    
    def test_password_hashing(self):
        """Тест хеширования пароля"""
        user = UserFactory()
        # Пароль должен быть зашифрован
        self.assertNotEqual(user.password, 'testpass123')
        self.assertTrue(user.check_password('testpass123'))


class UserRegistrationAPITest(BaseAPITestCase):
    """Тесты API регистрации пользователей"""
    
    def setUp(self):
        self.register_url = reverse('users:register')
        self.valid_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'Новый',
            'last_name': 'Пользователь',
            'password': 'StrongPassword123!',
            'role': 'engineer'
        }
    
    def test_user_registration_success(self):
        """Тест успешной регистрации пользователя"""
        response = self.client.post(self.register_url, self.valid_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Проверяем, что пользователь создан
        self.assertTrue(User.objects.filter(username='newuser').exists())
        user = User.objects.get(username='newuser')
        self.assertEqual(user.email, 'newuser@test.com')
        self.assertEqual(user.role, 'engineer')
    
    def test_user_registration_duplicate_username(self):
        """Тест регистрации с существующим именем пользователя"""
        UserFactory(username='existinguser')
        
        data = self.valid_data.copy()
        data['username'] = 'existinguser'
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)
    
    def test_user_registration_invalid_email(self):
        """Тест регистрации с невалидным email"""
        data = self.valid_data.copy()
        data['email'] = 'invalid-email'
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)
    
    def test_user_registration_weak_password(self):
        """Тест регистрации со слабым паролем"""
        data = self.valid_data.copy()
        data['password'] = '123'
        
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_user_registration_missing_required_fields(self):
        """Тест регистрации без обязательных полей"""
        response = self.client.post(self.register_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            self.assertIn(field, response.data)


class UserLoginAPITest(BaseAPITestCase):
    """Тесты API авторизации пользователей"""
    
    def setUp(self):
        self.login_url = reverse('users:login')
        self.user = UserFactory(username='testuser')
        self.user.set_password('testpass123')
        self.user.save()
    
    def test_user_login_success(self):
        """Тест успешной авторизации"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем наличие токенов
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
    
    def test_user_login_invalid_credentials(self):
        """Тест авторизации с неверными данными"""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_inactive_user(self):
        """Тест авторизации неактивного пользователя"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_login_missing_fields(self):
        """Тест авторизации без обязательных полей"""
        response = self.client.post(self.login_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileAPITest(BaseAPITestCase):
    """Тесты API профиля пользователя"""
    
    def setUp(self):
        self.user = UserFactory()
        self.profile_url = reverse('users:profile')
        self.authenticate(self.user)
    
    def test_get_user_profile(self):
        """Тест получения профиля пользователя"""
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем наличие данных пользователя
        self.assertEqual(response.data['id'], self.user.id)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['email'], self.user.email)
    
    def test_update_user_profile(self):
        """Тест обновления профиля пользователя"""
        data = {
            'first_name': 'Обновлённое',
            'last_name': 'Имя',
            'email': 'updated@test.com'
        }
        
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что данные обновились
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Обновлённое')
        self.assertEqual(self.user.last_name, 'Имя')
        self.assertEqual(self.user.email, 'updated@test.com')
    
    def test_update_profile_unauthenticated(self):
        """Тест обновления профиля неаутентифицированным пользователем"""
        self.logout()
        
        data = {'first_name': 'Обновлённое'}
        response = self.client.patch(self.profile_url, data)
        
        self.assert_permission_denied(response)
    
    def test_cannot_update_role(self):
        """Тест запрета изменения роли через профиль"""
        data = {'role': 'admin'}
        
        response = self.client.patch(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Роль не должна измениться
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.role, 'admin')


class UserPasswordChangeAPITest(BaseAPITestCase):
    """Тесты API смены пароля"""
    
    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('oldpassword123')
        self.user.save()
        self.change_password_url = reverse('users:change-password')
        self.authenticate(self.user)
    
    def test_change_password_success(self):
        """Тест успешной смены пароля"""
        data = {
            'old_password': 'oldpassword123',
            'new_password': 'NewPassword123!'
        }
        
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Проверяем, что пароль изменился
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('NewPassword123!'))
        self.assertFalse(self.user.check_password('oldpassword123'))
    
    def test_change_password_wrong_old_password(self):
        """Тест смены пароля с неверным старым паролем"""
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'NewPassword123!'
        }
        
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_change_password_weak_new_password(self):
        """Тест смены на слабый пароль"""
        data = {
            'old_password': 'oldpassword123',
            'new_password': '123'
        }
        
        response = self.client.post(self.change_password_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserPermissionsTest(BaseAPITestCase):
    """Тесты прав доступа пользователей"""
    
    def test_admin_can_access_admin_endpoints(self):
        """Тест доступа администратора к админским endpoints"""
        admin = AdminUserFactory()
        self.authenticate(admin)
        
        # Тестируем доступ к списку пользователей (только для админов)
        users_url = reverse('users:user-list')
        response = self.client.get(users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_regular_user_cannot_access_admin_endpoints(self):
        """Тест запрета доступа обычного пользователя к админским endpoints"""
        user = UserFactory()
        self.authenticate(user)
        
        users_url = reverse('users:user-list')
        response = self.client.get(users_url)
        self.assert_permission_denied(response)
    
    def test_manager_permissions(self):
        """Тест прав менеджера"""
        manager = ManagerUserFactory()
        self.authenticate(manager)
        
        # Менеджер должен иметь расширенные права
        # Проверяем доступ к созданию проектов
        projects_url = reverse('projects:project-list-create')
        response = self.client.get(projects_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class UserSecurityTest(BaseAPITestCase, SecurityTestMixin):
    """Тесты безопасности для модуля пользователей"""
    
    def test_password_security(self):
        """Тест безопасности паролей"""
        user = UserFactory()
        
        # Пароль должен быть зашифрован
        self.assertNotEqual(user.password, 'testpass123')
        self.assertNotIn('testpass123', user.password)
        
        # Проверяем хеширование
        self.assertTrue(user.password.startswith('pbkdf2_sha256$'))
    
    def test_sensitive_data_not_in_api_response(self):
        """Тест отсутствия чувствительных данных в API ответах"""
        user = UserFactory()
        self.authenticate(user)
        
        profile_url = reverse('users:profile')
        response = self.client.get(profile_url)
        
        # Пароль не должен возвращаться в API
        self.assertNotIn('password', response.data)
    
    def test_user_enumeration_protection(self):
        """Тест защиты от перечисления пользователей"""
        # При попытке входа с несуществующим пользователем
        # должна быть такая же ошибка, как и с неверным паролем
        login_url = reverse('users:login')
        
        # Несуществующий пользователь
        response1 = self.client.post(login_url, {
            'username': 'nonexistent',
            'password': 'password123'
        })
        
        # Существующий пользователь с неверным паролем
        UserFactory(username='existing')
        response2 = self.client.post(login_url, {
            'username': 'existing',
            'password': 'wrongpassword'
        })
        
        # Ответы должны быть одинаковыми
        self.assertEqual(response1.status_code, response2.status_code)


@pytest.mark.django_db
class TestUserModelPytest:
    """Pytest тесты для модели пользователя"""
    
    def test_user_creation_with_factory(self):
        """Тест создания пользователя через фабрику"""
        user = UserFactory()
        assert user.id is not None
        assert user.is_active is True
        assert user.username.startswith('user_')
    
    def test_admin_user_permissions(self):
        """Тест прав администратора"""
        admin = AdminUserFactory()
        assert admin.is_staff is True
        assert admin.is_superuser is True
        assert admin.role == 'admin'
    
    def test_user_unique_username(self):
        """Тест уникальности имени пользователя"""
        user1 = UserFactory(username='unique_user')
        
        # Создание пользователя с тем же именем должно вызвать ошибку
        with pytest.raises(Exception):
            UserFactory(username='unique_user')
    
    def test_user_email_format(self):
        """Тест формата email"""
        user = UserFactory()
        assert '@' in user.email
        assert user.email.endswith('@test.com')
