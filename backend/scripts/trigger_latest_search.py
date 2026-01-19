"""Trigger processing for the latest pending search"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search
from celery_app.tasks.search_tasks import process_search_task

async def trigger_latest():
    await connect_to_mongo()
    
    # Get latest pending search
    pending_searches = await Search.find(Search.status == "pending").sort(-Search.created_at).limit(1).to_list()
    
    if not pending_searches:
        print("❌ Нет pending поисков")
        return
    
    search = pending_searches[0]
    
    print("=" * 80)
    print("ЗАПУСК ОБРАБОТКИ ПОСЛЕДНЕГО ПОИСКА")
    print("=" * 80)
    print()
    print(f"ID: {search.id}")
    print(f"Запрос: {search.query[:80]}...")
    print(f"Город: {search.city}")
    print(f"Статус: {search.status}")
    print()
    
    print("Отправка задачи в Celery...")
    try:
        result = process_search_task.delay(str(search.id))
        print(f"✅ Задача отправлена!")
        print(f"   Task ID: {result.id}")
        print(f"   Статус: {result.state}")
        print()
        print("⏳ Ожидание обработки (10 секунд)...")
        
        import time
        time.sleep(10)
        
        # Check status again
        search = await Search.get(search.id)
        print()
        print(f"Новый статус: {search.status}")
        if search.status == "processing":
            print("✅ Поиск обрабатывается!")
        elif search.status == "completed":
            print("✅ Поиск завершен!")
        elif search.status == "failed":
            print(f"❌ Поиск завершился с ошибкой: {search.error_message}")
        else:
            print(f"⏳ Статус: {search.status}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(trigger_latest())
