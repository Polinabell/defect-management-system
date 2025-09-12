"""
Конфигурация Celery для системы управления дефектами
"""

import os
from celery import Celery
from django.conf import settings

# Устанавливаем переменную окружения для Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

# Создаем экземпляр Celery
app = Celery('defect_management')

# Используем строку конфигурации Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи в приложениях Django
app.autodiscover_tasks()

# Настройки для периодических задач
app.conf.beat_schedule = {
    # Резервное копирование базы данных - ежедневно в 2:00
    'backup-database-daily': {
        'task': 'apps.common.tasks.backup_database_task',
        'schedule': 60.0 * 60.0 * 24,  # Каждые 24 часа
    },
    
    # Очистка старых уведомлений - ежедневно в 3:00
    'cleanup-old-notifications': {
        'task': 'apps.common.tasks.cleanup_old_notifications_task',
        'schedule': 60.0 * 60.0 * 24,  # Каждые 24 часа
    },
    
    # Очистка старых записей аудита - еженедельно
    'cleanup-old-audit-logs': {
        'task': 'apps.common.tasks.cleanup_old_audit_logs_task',
        'schedule': 60.0 * 60.0 * 24 * 7,  # Каждые 7 дней
    },
    
    # Отправка ежедневных отчетов - каждый рабочий день в 9:00
    'send-daily-reports': {
        'task': 'apps.common.tasks.send_daily_reports_task',
        'schedule': 60.0 * 60.0 * 24,  # Каждые 24 часа
    },
    
    # Проверка просроченных дефектов - каждый час
    'check-overdue-defects': {
        'task': 'apps.common.tasks.check_overdue_defects_task',
        'schedule': 60.0 * 60.0,  # Каждый час
    },
    
    # Проверка состояния системы - каждые 15 минут
    'system-health-check': {
        'task': 'apps.common.tasks.system_health_check_task',
        'schedule': 60.0 * 15,  # Каждые 15 минут
    },
}

# Настройки для задач
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Moscow',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Обработчик сигналов для логирования
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


# Настройки для мониторинга
app.conf.update(
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Настройки для retry
app.conf.update(
    task_acks_late=True,
    worker_disable_rate_limits=False,
    task_reject_on_worker_lost=True,
)
