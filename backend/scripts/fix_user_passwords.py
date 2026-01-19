"""Fix user passwords - reset to known values"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.mongodb import connect_to_mongo
from app.domain.entities.user import User
from app.core.security import security_service

async def fix_passwords():
    """Reset passwords for test users"""
    await connect_to_mongo()
    
    print("=" * 80)
    print("ИСПРАВЛЕНИЕ ПАРОЛЕЙ ПОЛЬЗОВАТЕЛЕЙ")
    print("=" * 80)
    print()
    
    # Users to fix
    users_to_fix = [
        {"email": "admin@test.com", "password": "Admin123!"},
        {"email": "hr@test.com", "password": "Hr123456!"},
    ]
    
    for user_data in users_to_fix:
        try:
            user = await User.find_one({"email": user_data["email"]})
            if user:
                # Hash new password
                new_hash = security_service.get_password_hash(user_data["password"])
                user.hashed_password = new_hash
                await user.save()
                print(f"✓ Пароль обновлен для {user_data['email']}")
                print(f"  Новый пароль: {user_data['password']}")
            else:
                print(f"✗ Пользователь не найден: {user_data['email']}")
        except Exception as e:
            print(f"✗ Ошибка для {user_data['email']}: {e}")
    
    print()
    print("=" * 80)
    print("ГОТОВО!")
    print("=" * 80)
    print()
    print("Теперь можно войти с:")
    print("  admin@test.com / Admin123!")
    print("  hr@test.com / Hr123456!")

if __name__ == "__main__":
    asyncio.run(fix_passwords())
