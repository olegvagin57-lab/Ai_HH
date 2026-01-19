"""Check users in database"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.user import User

async def check():
    await connect_to_mongo()
    
    users = await User.find_all().to_list()
    
    print("=" * 80)
    print("ПОЛЬЗОВАТЕЛИ В БАЗЕ ДАННЫХ")
    print("=" * 80)
    print(f"Всего пользователей: {len(users)}")
    print()
    
    if not users:
        print("❌ Пользователей нет в базе!")
        print()
        print("Создайте пользователя через регистрацию на фронтенде или через API")
        return
    
    for i, user in enumerate(users, 1):
        print(f"Пользователь #{i}:")
        print(f"  ID: {user.id}")
        print(f"  Email: {user.email}")
        print(f"  Username: {user.username}")
        print(f"  Активен: {'✅' if user.is_active else '❌'}")
        print(f"  Роли: {', '.join(user.role_names) if user.role_names else 'нет'}")
        print()

if __name__ == "__main__":
    asyncio.run(check())
