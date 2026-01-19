"""Проверка, почему не найдены резюме"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.search import Search, Resume
from app.infrastructure.external.hh_client import hh_client

async def check():
    await connect_to_mongo()
    
    # Получить последний поиск
    search = await Search.find_all().sort(-Search.created_at).limit(1).to_list()
    if not search:
        print("Нет поисков")
        return
    
    search = search[0]
    print("=" * 80)
    print(f"ПОСЛЕДНИЙ ПОИСК: {search.id}")
    print("=" * 80)
    print(f"Запрос: {search.query}")
    print(f"Город: {search.city}")
    print(f"Статус: {search.status}")
    print(f"Найдено всего: {search.total_found}")
    print(f"Обработано: {search.processed_count}/{search.total_to_process}")
    print(f"Проанализировано: {search.analyzed_count}")
    if search.error_message:
        print(f"Ошибка: {search.error_message}")
    print()
    
    # Проверить резюме
    resumes = await Resume.find(Resume.search_id == str(search.id)).to_list()
    print(f"Резюме в базе: {len(resumes)}")
    print()
    
    # Проверить, работает ли парсер
    print("Тестирование парсера...")
    try:
        result = await hh_client.search_resumes(
            query=search.query,
            city=search.city,
            per_page=5,
            page=0
        )
        print(f"Результат парсера:")
        print(f"  Найдено: {result.get('found', 0)}")
        print(f"  Страниц: {result.get('pages', 0)}")
        print(f"  Резюме на странице: {len(result.get('items', []))}")
        
        if result.get('items'):
            print("\nПримеры найденных резюме:")
            for i, item in enumerate(result.get('items', [])[:3], 1):
                resume_id = item.get('id', 'N/A')
                name = f"{item.get('first_name', '')} {item.get('last_name', '')}".strip() or 'N/A'
                title = item.get('title', 'N/A')
                print(f"  {i}. ID: {resume_id}, Имя: {name}, Должность: {title}")
        else:
            print("\n⚠️ Парсер не вернул резюме!")
            print("Возможные причины:")
            print("  1. Парсер заблокирован HH.ru")
            print("  2. Нет резюме по такому запросу")
            print("  3. Ошибка в парсере")
    except Exception as e:
        print(f"❌ Ошибка при тестировании парсера: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(check())
