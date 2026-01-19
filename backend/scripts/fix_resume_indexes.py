"""Fix resume indexes to allow same hh_id in different searches"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def fix_indexes():
    """Fix resume indexes"""
    await connect_to_mongo()
    
    from app.config import settings
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    collection = db["resumes"]
    
    print("Проверка текущих индексов...")
    indexes = await collection.list_indexes().to_list(length=None)
    for idx in indexes:
        print(f"  - {idx.get('name')}: {idx.get('key')}")
    
    print("\nУдаление старого уникального индекса на hh_id...")
    try:
        await collection.drop_index("hh_id_1")
        print("  ✅ Индекс hh_id_1 удален")
    except Exception as e:
        print(f"  ⚠️  Ошибка удаления индекса: {e}")
    
    print("\nСоздание нового индекса на hh_id (без уникальности)...")
    try:
        await collection.create_index("hh_id", name="hh_id_1", sparse=True)
        print("  ✅ Индекс hh_id_1 создан (не уникальный)")
    except Exception as e:
        print(f"  ⚠️  Ошибка создания индекса: {e}")
    
    print("\nСоздание уникального индекса на комбинацию search_id + hh_id...")
    try:
        await collection.create_index(
            [("search_id", 1), ("hh_id", 1)],
            name="search_id_hh_id_1",
            unique=True,
            sparse=True
        )
        print("  ✅ Уникальный индекс search_id_hh_id_1 создан")
    except Exception as e:
        print(f"  ⚠️  Ошибка создания индекса: {e}")
    
    print("\nПроверка новых индексов...")
    indexes = await collection.list_indexes().to_list(length=None)
    for idx in indexes:
        print(f"  - {idx.get('name')}: {idx.get('key')}, unique={idx.get('unique', False)}")
    
    print("\n✅ Индексы обновлены!")
    print("Теперь одно резюме (hh_id) может быть в разных поисках (search_id)")

if __name__ == "__main__":
    asyncio.run(fix_indexes())
