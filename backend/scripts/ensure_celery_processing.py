"""Ensure Celery tasks are processed automatically"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery_app.celery import celery_app
from celery_app.tasks.search_tasks import process_search_task

def check_celery_setup():
    """Check and fix Celery setup for automatic processing"""
    print("=" * 80)
    print("ПРОВЕРКА НАСТРОЙКИ CELERY ДЛЯ АВТОМАТИЧЕСКОЙ ОБРАБОТКИ")
    print("=" * 80)
    print()
    
    # Check registered tasks
    registered = [t for t in celery_app.tasks.keys() if not t.startswith('celery.')]
    print(f"Зарегистрированные задачи: {len(registered)}")
    for task in registered[:5]:
        print(f"  - {task}")
    
    # Check if process_search is registered
    if "process_search" in registered or "celery_app.tasks.search_tasks.process_search" in registered:
        print("\n✓ Задача process_search зарегистрирована")
    else:
        print("\n✗ Задача process_search НЕ зарегистрирована!")
        print("  Проблема: задача не найдена в списке зарегистрированных")
        return False
    
    # Check worker connection
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            print(f"\n✓ Celery worker'ы активны: {len(stats)}")
            for worker_name in stats.keys():
                print(f"  - {worker_name}")
            
            # Check active queues
            active_queues = inspect.active_queues()
            if active_queues:
                print("\n✓ Очереди активны:")
                for worker, queues in active_queues.items():
                    for queue in queues:
                        queue_name = queue.get('name', 'unknown')
                        print(f"  - {worker}: {queue_name}")
                        if queue_name != 'celery':
                            print(f"    ⚠ Worker слушает очередь '{queue_name}', а не 'celery'")
        else:
            print("\n✗ Нет активных Celery worker'ов!")
            print("  Решение: запустите worker командой:")
            print("    celery -A celery_app.celery worker --loglevel=info")
            return False
    except Exception as e:
        print(f"\n✗ Ошибка проверки worker'ов: {e}")
        return False
    
    # Check configuration
    print("\nКонфигурация Celery:")
    print(f"  Broker: {celery_app.conf.broker_url}")
    print(f"  Backend: {celery_app.conf.result_backend}")
    print(f"  Default queue: {celery_app.conf.task_default_queue}")
    print(f"  Default exchange: {celery_app.conf.task_default_exchange}")
    print(f"  Default routing key: {celery_app.conf.task_default_routing_key}")
    
    print("\n" + "=" * 80)
    print("РЕКОМЕНДАЦИИ:")
    print("=" * 80)
    print()
    print("1. Убедитесь, что Celery worker запущен:")
    print("   celery -A celery_app.celery worker --loglevel=info")
    print()
    print("2. Worker должен слушать очередь 'celery'")
    print()
    print("3. Проверьте логи worker'а на наличие ошибок")
    print()
    print("4. Если задачи не обрабатываются, перезапустите worker:")
    print("   powershell -ExecutionPolicy Bypass -File scripts/restart_celery.ps1")
    print()
    
    return True

if __name__ == "__main__":
    check_celery_setup()
