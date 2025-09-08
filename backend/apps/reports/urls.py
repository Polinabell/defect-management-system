"""
URL маршруты для отчётов и аналитики
"""

from django.urls import path
from . import views

app_name = 'reports'

# Маршруты для шаблонов отчётов
template_urlpatterns = [
    path('templates/', views.ReportTemplateListCreateView.as_view(), name='template-list-create'),
    path('templates/<int:pk>/', views.ReportTemplateDetailView.as_view(), name='template-detail'),
]

# Маршруты для сгенерированных отчётов
report_urlpatterns = [
    path('generated/', views.GeneratedReportListView.as_view(), name='report-list'),
    path('generated/<int:pk>/', views.GeneratedReportDetailView.as_view(), name='report-detail'),
    path('generate/', views.GenerateReportView.as_view(), name='generate-report'),
    path('download/<int:report_id>/', views.DownloadReportView.as_view(), name='download-report'),
]

# Маршруты для дашбордов
dashboard_urlpatterns = [
    path('dashboards/', views.DashboardListCreateView.as_view(), name='dashboard-list-create'),
    path('dashboards/<int:pk>/', views.DashboardDetailView.as_view(), name='dashboard-detail'),
]

# Маршруты для аналитических запросов
query_urlpatterns = [
    path('queries/', views.AnalyticsQueryListCreateView.as_view(), name='query-list-create'),
    path('queries/<int:pk>/', views.AnalyticsQueryDetailView.as_view(), name='query-detail'),
    path('queries/execute/', views.ExecuteQueryView.as_view(), name='execute-query'),
]

# Маршруты для аналитики
analytics_urlpatterns = [
    path('analytics/project/<int:project_id>/', views.project_analytics, name='project-analytics'),
    path('analytics/user/', views.user_performance, name='user-performance'),
    path('analytics/user/<int:user_id>/', views.user_performance, name='user-performance-detail'),
    path('analytics/system/', views.system_analytics, name='system-analytics'),
]

# Дополнительные маршруты
additional_urlpatterns = [
    path('export/', views.ExportDataView.as_view(), name='export-data'),
    path('charts/', views.chart_data, name='chart-data'),
]

urlpatterns = (
    template_urlpatterns + 
    report_urlpatterns + 
    dashboard_urlpatterns + 
    query_urlpatterns + 
    analytics_urlpatterns + 
    additional_urlpatterns
)
