"""
URL маршруты для управления дефектами
"""

from django.urls import path, include
from . import views

app_name = 'defects'

# Маршруты для категорий дефектов
category_urlpatterns = [
    path('categories/', views.DefectCategoryListView.as_view(), name='category-list-create'),
    path('categories/<int:pk>/', views.DefectCategoryDetailView.as_view(), name='category-detail'),
]

# Основные маршруты дефектов
defect_urlpatterns = [
    path('', views.DefectListCreateView.as_view(), name='defect-list-create'),
    path('<int:pk>/', views.DefectDetailView.as_view(), name='defect-detail'),
    path('<int:defect_id>/status/', views.DefectStatusChangeView.as_view(), name='defect-status-change'),
    path('<int:defect_id>/assign/', views.DefectAssignmentView.as_view(), name='defect-assignment'),
    path('<int:defect_pk>/files/', views.DefectFilesView.as_view(), name='defect-files'),
    path('<int:defect_pk>/files/<int:pk>/', views.DefectFileDetailView.as_view(), name='defect-file-detail'),
    path('<int:defect_pk>/comments/', views.DefectCommentsView.as_view(), name='defect-comments'),
    path('<int:defect_pk>/comments/<int:pk>/', views.DefectCommentDetailView.as_view(), name='defect-comment-detail'),
    path('<int:defect_pk>/history/', views.DefectHistoryView.as_view(), name='defect-history'),
]

# Дополнительные маршруты
additional_urlpatterns = [
    path('search/', views.DefectSearchView.as_view(), name='defect-search'),
    path('stats/', views.defect_stats, name='defect-stats'),
    path('bulk-update/', views.bulk_update_defects, name='bulk-update-defects'),
]

urlpatterns = category_urlpatterns + defect_urlpatterns + additional_urlpatterns
