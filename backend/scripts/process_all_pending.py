"""Process all pending searches"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search
from celery_app.tasks.search_tasks import process_search_task

async def process_all():
    await connect_to_mongo()
    
    # Get all pending searches
    pending_searches = await Search.find(Search.status == "pending").sort(-Search.created_at).to_list()
    
    print("=" * 80)
    print("ОБРАБОТКА ВСЕХ PENDING ПОИСКОВ")
    print("=" * 80)
    print()
    print(f"Найдено pending поисков: {len(pending_searches)}")
    print()
    
    if not pending_searches:
        print("✅ Нет pending поисков")
        return
    
    triggered = 0
    for i, search in enumerate(pending_searches, 1):
        print(f"[{i}/{len(pending_searches)}] Запуск поиска {search.id}...")
        try:
            result = process_search_task.delay(str(search.id))
            print(f"  ✅ Задача отправлена: {result.id}")
            triggered += 1
        except Exception as e:
            print(f"  ❌ Ошибка: {e}")
    
    print()
    print("=" * 80)
    print(f"✅ Запущено обработок: {triggered}/{len(pending_searches)}")
    print("=" * 80)
    print()
    print("⏳ Проверьте статус через несколько секунд:")
    print("   python scripts/check_search_status.py")
    print()
    print("💡 В окне Celery worker вы должны увидеть логи обработки")

if __name__ == "__main__":
    asyncio.run(process_all())
