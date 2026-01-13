#!/usr/bin/env python3
"""
Простой скрипт для создания тестового пользователя
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def create_test_user():
    """Создание тестового пользователя"""
    try:
        from app.database.mongodb import connect_to_mongo, close_mongo_connection
        from app.models.user_mongo import User
        from app.core.security import security_service
        
        print("Подключение к MongoDB...")
        await connect_to_mongo()
        print("[OK] Подключено")
        
        # Проверяем, есть ли уже админ
        admin = await User.find_one({"email": "admin@test.com"})
        if admin:
            print(f"[OK] Администратор уже существует: {admin.email}")
            print(f"   Пароль: admin123")
        else:
            # Создаем администратора
            admin = User(
                email="admin@test.com",
                username="admin",
                hashed_password=security_service.get_password_hash("admin123"),
                full_name="Тестовый Администратор",
                company_name="Тестовая Компания",
                position="Администратор",
                role_names=["admin"],
                is_active=True,
                is_verified=True
            )
            await admin.insert()
            print("[OK] Администратор создан")
        
        # Создаем HR специалиста
        hr = await User.find_one({"email": "hr@test.com"})
        if hr:
            print(f"[OK] HR специалист уже существует: {hr.email}")
            print(f"   Пароль: hr123")
        else:
            hr = User(
                email="hr@test.com",
                username="hr",
                hashed_password=security_service.get_password_hash("hr123"),
                full_name="HR Специалист",
                company_name="Тестовая Компания",
                position="HR Специалист",
                role_names=["hr_specialist"],
                is_active=True,
                is_verified=True
            )
            await hr.insert()
            print("[OK] HR специалист создан")
        
        print("\n" + "="*50)
        print("ДАННЫЕ ДЛЯ ВХОДА:")
        print("="*50)
        print("\nАДМИНИСТРАТОР:")
        print("   Email: admin@test.com")
        print("   Пароль: admin123")
        print("\nHR СПЕЦИАЛИСТ:")
        print("   Email: hr@test.com")
        print("   Пароль: hr123")
        print("\n" + "="*50)
        
        await close_mongo_connection()
        return True
        
    except Exception as e:
        print(f"[ERROR] Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(create_test_user())
