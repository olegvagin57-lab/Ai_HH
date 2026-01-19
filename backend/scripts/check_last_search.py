"""Check last search status and error"""
import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search

async def check():
    await connect_to_mongo()
    
    # Get last search
    searches = await Search.find_all().sort('-created_at').limit(1).to_list()
    
    if not searches:
        print("❌ Нет поисков в базе данных")
        return
    
    search = searches[0]
    
    print("=" * 80)
    print("ПОСЛЕДНИЙ ПОИСК")
    print("=" * 80)
    print(f"ID: {search.id}")
    print(f"Статус: {search.status}")
    print(f"Запрос: {search.query[:100]}...")
    print(f"Город: {search.city}")
    print(f"Создан: {search.created_at}")
    print(f"Найдено резюме: {search.total_found}")
    print(f"Проанализировано: {search.analyzed_count}")
    
    if search.error_message:
        print(f"\n❌ ОШИБКА:")
        print(f"{search.error_message}")
    
    if search.completed_at:
        print(f"Завершен: {search.completed_at}")
    
    print("=" * 80)
    
    # Get all failed searches
    failed_searches = await Search.find_all(Search.status == "failed").sort('-created_at').limit(5).to_list()
    
    if failed_searches:
        print(f"\nПоследние 5 неудачных поисков:")
        for i, s in enumerate(failed_searches, 1):
            print(f"\n{i}. ID: {s.id}")
            print(f"   Запрос: {s.query[:50]}...")
            print(f"   Ошибка: {s.error_message[:200] if s.error_message else 'N/A'}")

if __name__ == "__main__":
    asyncio.run(check())
