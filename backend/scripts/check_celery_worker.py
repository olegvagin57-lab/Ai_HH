"""Check Celery worker status and manually trigger pending searches"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search
from celery_app.tasks.search_tasks import process_search_task

async def check_and_trigger():
    await connect_to_mongo()
    
    # Get pending searches
    pending_searches = await Search.find(Search.status == "pending").to_list()
    
    print("=" * 80)
    print("ПРОВЕРКА CELERY WORKER И PENDING ПОИСКОВ")
    print("=" * 80)
    print()
    print(f"Найдено pending поисков: {len(pending_searches)}")
    print()
    
    if not pending_searches:
        print("✅ Нет pending поисков")
        return
    
    for i, search in enumerate(pending_searches[:5], 1):
        print(f"Поиск #{i}:")
        print(f"  ID: {search.id}")
        print(f"  Запрос: {search.query[:60]}...")
        print(f"  Город: {search.city}")
        print(f"  Статус: {search.status}")
        print(f"  Создан: {search.created_at}")
        print()
    
    # Try to trigger manually
    print("=" * 80)
    print("ПОПЫТКА ЗАПУСТИТЬ ОБРАБОТКУ ВРУЧНУЮ")
    print("=" * 80)
    print()
    
    for search in pending_searches[:3]:
        print(f"Запуск обработки для поиска {search.id}...")
        try:
            # Trigger task directly
            result = process_search_task.delay(str(search.id))
            print(f"  ✅ Задача отправлена в очередь: {result.id}")
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
        print()

if __name__ == "__main__":
    asyncio.run(check_and_trigger())
