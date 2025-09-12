#!/usr/bin/env python
"""
Скрипт для запуска Celery worker и beat
"""

import os
import sys
import subprocess
from pathlib import Path

# Добавляем путь к Django проекту
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Устанавливаем переменную окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

def start_celery_worker():
    """Запускает Celery worker"""
    cmd = [
        'celery',
        '-A', 'config',
        'worker',
        '--loglevel=info',
        '--concurrency=4',
        '--pool=prefork'
    ]
    
    print("Запуск Celery worker...")
    subprocess.run(cmd)

def start_celery_beat():
    """Запускает Celery beat"""
    cmd = [
        'celery',
        '-A', 'config',
        'beat',
        '--loglevel=info',
        '--scheduler=django_celery_beat.schedulers:DatabaseScheduler'
    ]
    
    print("Запуск Celery beat...")
    subprocess.run(cmd)

def start_celery_flower():
    """Запускает Celery Flower для мониторинга"""
    cmd = [
        'celery',
        '-A', 'config',
        'flower',
        '--port=5555'
    ]
    
    print("Запуск Celery Flower...")
    subprocess.run(cmd)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Управление Celery')
    parser.add_argument('command', choices=['worker', 'beat', 'flower', 'all'], 
                       help='Команда для выполнения')
    
    args = parser.parse_args()
    
    if args.command == 'worker':
        start_celery_worker()
    elif args.command == 'beat':
        start_celery_beat()
    elif args.command == 'flower':
        start_celery_flower()
    elif args.command == 'all':
        print("Запуск всех сервисов Celery...")
        print("Для полного запуска используйте:")
        print("python start_celery.py worker &")
        print("python start_celery.py beat &")
        print("python start_celery.py flower &")
