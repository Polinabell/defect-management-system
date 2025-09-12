"""
Тесты для валидаторов
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from apps.common.validators import (
    validate_safe_string, validate_file_extension, validate_file_size,
    validate_password_strength, validate_phone_number, validate_email_domain,
    validate_no_sql_injection, validate_no_xss
)


class ValidatorsTest(TestCase):
    """Тесты для валидаторов"""
    
    def test_validate_safe_string(self):
        """Тест валидатора безопасных строк"""
        # Валидные строки
        validate_safe_string("Обычная строка")
        validate_safe_string("Строка с цифрами 123")
        validate_safe_string("Строка с пробелами")
        
        # Невалидные строки
        with self.assertRaises(ValidationError):
            validate_safe_string("Строка с <script>")
        
        with self.assertRaises(ValidationError):
            validate_safe_string("Строка с 'кавычками'")
        
        with self.assertRaises(ValidationError):
            validate_safe_string("Строка с & амперсандом")
    
    def test_validate_file_extension(self):
        """Тест валидатора расширений файлов"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Валидные расширения
        valid_file = SimpleUploadedFile("test.jpg", b"file content")
        validate_file_extension(valid_file)
        
        valid_file = SimpleUploadedFile("document.pdf", b"file content")
        validate_file_extension(valid_file)
        
        # Невалидные расширения
        invalid_file = SimpleUploadedFile("malicious.exe", b"file content")
        with self.assertRaises(ValidationError):
            validate_file_extension(invalid_file)
    
    def test_validate_file_size(self):
        """Тест валидатора размера файла"""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        # Валидный размер (1MB)
        valid_file = SimpleUploadedFile("test.jpg", b"x" * (1024 * 1024))
        validate_file_size(valid_file)
        
        # Невалидный размер (11MB)
        invalid_file = SimpleUploadedFile("large.jpg", b"x" * (11 * 1024 * 1024))
        with self.assertRaises(ValidationError):
            validate_file_size(invalid_file)
    
    def test_validate_password_strength(self):
        """Тест валидатора силы пароля"""
        # Валидный пароль
        validate_password_strength("StrongPass123!")
        
        # Невалидные пароли
        with self.assertRaises(ValidationError):
            validate_password_strength("short")  # Слишком короткий
        
        with self.assertRaises(ValidationError):
            validate_password_strength("nouppercase123!")  # Нет заглавных букв
        
        with self.assertRaises(ValidationError):
            validate_password_strength("NOLOWERCASE123!")  # Нет строчных букв
        
        with self.assertRaises(ValidationError):
            validate_password_strength("NoNumbers!")  # Нет цифр
        
        with self.assertRaises(ValidationError):
            validate_password_strength("NoSpecialChars123")  # Нет спец. символов
    
    def test_validate_phone_number(self):
        """Тест валидатора номера телефона"""
        # Валидные номера
        validate_phone_number("+7 (999) 123-45-67")
        validate_phone_number("8 999 123 45 67")
        validate_phone_number("79991234567")
        
        # Невалидные номера
        with self.assertRaises(ValidationError):
            validate_phone_number("123")  # Слишком короткий
        
        with self.assertRaises(ValidationError):
            validate_phone_number("abc-def-ghi")  # Буквы
    
    def test_validate_email_domain(self):
        """Тест валидатора домена email"""
        # Валидные домены
        validate_email_domain("user@gmail.com")
        validate_email_domain("user@company.ru")
        
        # Невалидные домены
        with self.assertRaises(ValidationError):
            validate_email_domain("user@tempmail.com")  # Временный email
    
    def test_validate_no_sql_injection(self):
        """Тест валидатора против SQL инъекций"""
        # Валидные строки
        validate_no_sql_injection("Обычная строка")
        validate_no_sql_injection("SELECT * FROM users")  # Вне контекста
        
        # Невалидные строки
        with self.assertRaises(ValidationError):
            validate_no_sql_injection("'; DROP TABLE users; --")
        
        with self.assertRaises(ValidationError):
            validate_no_sql_injection("1' OR '1'='1")
        
        with self.assertRaises(ValidationError):
            validate_no_sql_injection("UNION SELECT * FROM passwords")
    
    def test_validate_no_xss(self):
        """Тест валидатора против XSS"""
        # Валидные строки
        validate_no_xss("Обычная строка")
        validate_no_xss("Текст с <b>HTML</b> тегами")
        
        # Невалидные строки
        with self.assertRaises(ValidationError):
            validate_no_xss("<script>alert('XSS')</script>")
        
        with self.assertRaises(ValidationError):
            validate_no_xss("<iframe src='malicious.com'></iframe>")
        
        with self.assertRaises(ValidationError):
            validate_no_xss("javascript:alert('XSS')")
        
        with self.assertRaises(ValidationError):
            validate_no_xss("<img onload='alert(1)'>")
