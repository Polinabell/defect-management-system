"""
URL Configuration для системы управления дефектами
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status

def health_check(request):
    """Базовый health check endpoint"""
    return JsonResponse({
        'status': 'healthy',
        'version': '1.0.0',
        'environment': getattr(settings, 'ENVIRONMENT', 'unknown')
    })

def serve_frontend(request):
    """Обслуживание фронтенда React"""
    return render(request, 'index.html')

# API patterns
api_patterns = [
    # path('auth/', include('apps.users.urls')),
    # path('users/', include('apps.users.urls')),
    # path('projects/', include('apps.projects.urls')),
    # path('defects/', include('apps.defects.urls')),
    # path('reports/', include('apps.reports.urls')),
]

# Main URL patterns
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health check
    path('health/', health_check, name='health-check'),

    # API v1
    path('api/v1/', include(api_patterns)),

    # Frontend (главная страница)
    path('', serve_frontend, name='frontend'),
]

# Media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Debug toolbar in development
if settings.DEBUG and 'debug_toolbar' in settings.INSTALLED_APPS:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

# Silk profiler in development
if settings.DEBUG and 'silk' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('silk/', include('silk.urls', namespace='silk'))
    ]

# Health check endpoints in production
if 'health_check' in settings.INSTALLED_APPS:
    urlpatterns += [
        path('health/', include('health_check.urls')),
    ]

# Custom error handlers
handler400 = 'apps.common.views.bad_request'
handler403 = 'apps.common.views.permission_denied'
handler404 = 'apps.common.views.not_found'
handler500 = 'apps.common.views.server_error'
