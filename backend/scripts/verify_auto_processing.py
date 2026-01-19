"""Verify that tasks are automatically processed"""
import asyncio
import sys
import os
import httpx
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery_app.tasks.search_tasks import process_search_task
from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search

async def test():
    await connect_to_mongo()
    
    print("=" * 80)
    print("ПРОВЕРКА АВТОМАТИЧЕСКОЙ ОБРАБОТКИ")
    print("=" * 80)
    print()
    
    # Get latest pending search
    search = await Search.find_one(Search.status == "pending")
    
    if not search:
        print("Нет pending поисков для тестирования")
        return
    
    print(f"Тестируем поиск: {search.id}")
    print(f"Запрос: {search.query[:60]}...")
    print()
    
    # Send task using apply_async (same as in API)
    print("Отправка задачи через apply_async...")
    try:
        task_result = process_search_task.apply_async(
            args=[str(search.id)],
            countdown=0
        )
        print(f"Задача отправлена: {task_result.id}")
        print()
        
        # Wait and check status
        print("Ожидание обработки (15 секунд)...")
        for i in range(5):
            await asyncio.sleep(3)
            await search.reload() if hasattr(search, 'reload') else None
            search = await Search.get(search.id)
            status = search.status
            print(f"  [{i*3+3}s] Статус: {status}")
            
            if status == "processing":
                print("  ✓ Задача обрабатывается!")
                break
            elif status == "completed":
                print("  ✓ Задача завершена!")
                break
            elif status == "failed":
                print(f"  ✗ Задача завершилась с ошибкой: {search.error_message}")
                break
        
        if search.status == "pending":
            print()
            print("⚠ Задача все еще pending. Проверьте:")
            print("  1. Celery worker запущен?")
            print("  2. Worker видит задачи? (python scripts/test_celery_connection.py)")
            print("  3. Есть ли ошибки в логах worker?")
    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
