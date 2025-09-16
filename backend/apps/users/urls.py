"""
URL маршруты для пользователей и аутентификации
"""

from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'users'

# Authentication URLs
auth_urlpatterns = [
    path('login/', views.CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password-reset-confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]

# User management URLs
user_urlpatterns = [
    path('', views.UserListCreateView.as_view(), name='user-list-create'),
    path('<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('me/profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('me/sessions/', views.UserSessionsView.as_view(), name='user-sessions'),
    path('sessions/<int:session_id>/terminate/', views.TerminateSessionView.as_view(), name='terminate-session'),
    path('stats/', views.user_stats, name='user-stats'),
    path('<int:user_id>/unlock/', views.unlock_user, name='unlock-user'),
    path('<int:user_id>/reset-password/', views.reset_user_password, name='reset-user-password'),
]

urlpatterns = [
    # Группируем маршруты по функциональности
    path('auth/', include(auth_urlpatterns)),
    path('', include(user_urlpatterns)),
]
