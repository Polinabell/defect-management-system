"""
Настройки для разработки
"""

from .base import *

# Debug settings
DEBUG = True
ALLOWED_HOSTS = ['*']

# Development specific apps
INSTALLED_APPS += [
    'debug_toolbar',
    'silk',
    'django_extensions',
]

# Development middleware
MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'silk.middleware.SilkMiddleware',
]

# Debug toolbar settings
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: DEBUG,
}

# Database для разработки - можно использовать SQLite для простоты
if config('USE_SQLITE', default=False, cast=bool):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# CORS для разработки
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Email backend для разработки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Отключаем HTTPS требования для разработки
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Логирование для разработки
LOGGING['handlers']['console']['level'] = 'DEBUG'
LOGGING['loggers']['apps']['level'] = 'DEBUG'

# Отключаем кэширование для разработки
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Silk configuration для профилирования
SILKY_PYTHON_PROFILER = True
SILKY_PYTHON_PROFILER_BINARY = True
