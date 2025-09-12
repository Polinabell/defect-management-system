"""
Конфигурация расписания для Celery Beat
"""

from celery.schedules import crontab

# Расписание периодических задач
CELERY_BEAT_SCHEDULE = {
    # Резервное копирование базы данных - ежедневно в 2:00
    'backup-database-daily': {
        'task': 'apps.common.tasks.backup_database_task',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Очистка старых уведомлений - ежедневно в 3:00
    'cleanup-old-notifications': {
        'task': 'apps.common.tasks.cleanup_old_notifications_task',
        'schedule': crontab(hour=3, minute=0),
    },
    
    # Очистка старых записей аудита - еженедельно по воскресеньям в 4:00
    'cleanup-old-audit-logs': {
        'task': 'apps.common.tasks.cleanup_old_audit_logs_task',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
    },
    
    # Отправка ежедневных отчетов - каждый рабочий день в 9:00
    'send-daily-reports': {
        'task': 'apps.common.tasks.send_daily_reports_task',
        'schedule': crontab(hour=9, minute=0, day_of_week='1-5'),
    },
    
    # Проверка просроченных дефектов - каждый час
    'check-overdue-defects': {
        'task': 'apps.common.tasks.check_overdue_defects_task',
        'schedule': crontab(minute=0),
    },
    
    # Проверка состояния системы - каждые 15 минут
    'system-health-check': {
        'task': 'apps.common.tasks.system_health_check_task',
        'schedule': crontab(minute='*/15'),
    },
}
