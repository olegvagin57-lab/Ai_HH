"""Check Celery worker status and manually trigger search if needed"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search
from celery_app.tasks.search_tasks import process_search_task

async def check_and_trigger():
    await connect_to_mongo()
    
    # Get latest pending search
    latest = await Search.find_all(Search.status == "pending").sort('-created_at').limit(1).to_list()
    if latest:
        latest = latest[0]
    else:
        latest = None
    
    if not latest:
        print("✅ Нет ожидающих поисков")
        return
    
    print("=" * 80)
    print("НАЙДЕН ОЖИДАЮЩИЙ ПОИСК")
    print("=" * 80)
    print(f"ID: {latest.id}")
    print(f"Запрос: {latest.query[:80]}...")
    print(f"Город: {latest.city}")
    print(f"Создан: {latest.created_at}")
    print()
    
    # Try to trigger manually
    print("Попытка запустить задачу вручную...")
    try:
        result = process_search_task.delay(str(latest.id))
        print(f"✅ Задача запущена! Task ID: {result.id}")
        print()
        print("Проверьте статус через несколько секунд:")
        print(f"  python scripts/check_search_status.py")
    except Exception as e:
        print(f"❌ Ошибка запуска задачи: {e}")
        print()
        print("Возможные причины:")
        print("  1. Celery worker не запущен")
        print("  2. Redis недоступен")
        print("  3. Проблемы с подключением")
        print()
        print("Решение:")
        print("  1. Запустите Celery worker:")
        print("     celery -A celery_app.celery worker --loglevel=info")
        print("  2. Проверьте Redis:")
        print("     redis-cli ping")

if __name__ == "__main__":
    asyncio.run(check_and_trigger())
