"""
Настройки для тестирования
"""

from .base import *

# Test settings
DEBUG = False
TESTING = True

# Use in-memory database for tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Fast password hashing for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Disable Celery for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Media files for tests
MEDIA_ROOT = '/tmp/test_media'

# Logging for tests
LOGGING['loggers']['apps']['level'] = 'CRITICAL'
LOGGING['handlers']['console']['level'] = 'CRITICAL'

# REST Framework for tests
REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] = [
    'rest_framework.authentication.SessionAuthentication',
    'rest_framework_simplejwt.authentication.JWTAuthentication',
]

# JWT settings for tests
SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'] = timedelta(minutes=5)
SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'] = timedelta(minutes=10)

# Disable security features for tests
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
