"""Manually trigger search processing"""
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search
from celery_app.tasks.search_tasks import process_search_task

async def trigger():
    await connect_to_mongo()
    
    # Get latest pending search - use ID from check_search_status output
    # Latest search ID: 696e692256a47ad92c57db48
    search_id = "696e692256a47ad92c57db48"
    
    try:
        latest = await Search.get(search_id)
    except:
        # Try to find any pending search
        all_searches = await Search.find_all().to_list()
        pending = [s for s in all_searches if s.status == "pending"]
        if pending:
            latest = max(pending, key=lambda x: x.created_at)
            search_id = str(latest.id)
        else:
            print("❌ Нет ожидающих поисков")
            return
    
    print("=" * 80)
    print("ЗАПУСК ОБРАБОТКИ ПОИСКА")
    print("=" * 80)
    print(f"ID: {latest.id}")
    print(f"Запрос: {latest.query[:80]}...")
    print(f"Город: {latest.city}")
    print()
    
    # Trigger task directly (synchronous call for testing)
    print("Запуск обработки...")
    try:
        # Call task directly (will run synchronously)
        result = process_search_task(str(latest.id))
        print(f"✅ Обработка завершена!")
        print(f"Результат: {result}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trigger())
