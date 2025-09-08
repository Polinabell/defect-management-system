"""
URL маршруты для управления проектами
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'projects'

# Основные маршруты проектов
project_urlpatterns = [
    path('', views.ProjectListCreateView.as_view(), name='project-list-create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('<int:project_pk>/members/', views.ProjectMembersView.as_view(), name='project-members'),
    path('<int:project_pk>/members/add/', views.AddProjectMemberView.as_view(), name='add-project-member'),
    path('<int:project_pk>/members/<int:user_pk>/remove/', views.RemoveProjectMemberView.as_view(), name='remove-project-member'),
    path('<int:project_pk>/stages/', views.ProjectStagesView.as_view(), name='project-stages'),
    path('<int:project_pk>/stages/<int:pk>/', views.ProjectStageDetailView.as_view(), name='project-stage-detail'),
    path('<int:project_pk>/clone/', views.clone_project, name='clone-project'),
]

# Маршруты для шаблонов проектов
template_urlpatterns = [
    path('templates/', views.ProjectTemplatesView.as_view(), name='project-templates'),
    path('templates/<int:pk>/', views.ProjectTemplateDetailView.as_view(), name='project-template-detail'),
]

# Дополнительные маршруты
additional_urlpatterns = [
    path('search/', views.ProjectSearchView.as_view(), name='project-search'),
    path('stats/', views.project_stats, name='project-stats'),
]

urlpatterns = project_urlpatterns + template_urlpatterns + additional_urlpatterns
