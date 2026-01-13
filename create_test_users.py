#!/usr/bin/env python3
"""
Создание тестовых пользователей для системы HH Resume Analyzer
"""

import asyncio
import sys
import os
from datetime import datetime

# Добавляем путь к backend в PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

async def create_test_users():
    """Создание тестовых пользователей"""
    print("👥 Создание тестовых пользователей...")
    print("=" * 50)
    
    try:
        # Импорты
        from app.database.mongodb import connect_to_mongo, mongodb
        from app.models.user_mongo import User, Role, Permission
        from app.services.user_service_mongo import UserService
        from app.core.security import security_service
        
        # Подключаемся к MongoDB
        print("🔗 Подключение к MongoDB...")
        await connect_to_mongo()
        print("✅ Подключение успешно")
        
        # Создаем сервис пользователей
        user_service = UserService()
        
        # Проверяем, есть ли уже пользователи
        existing_users = await User.find_all().to_list()
        if existing_users:
            print(f"⚠️ Найдено {len(existing_users)} существующих пользователей:")
            for user in existing_users:
                print(f"   - {user.email} ({user.role})")
            
            response = input("\n❓ Удалить всех существующих пользователей? (y/N): ")
            if response.lower() == 'y':
                await User.delete_all()
                print("🗑️ Все пользователи удалены")
            else:
                print("⏭️ Пропускаем создание пользователей")
                return
        
        # Создаем тестовых пользователей
        test_users = [
            {
                "email": "admin@hh-analyzer.com",
                "password": "admin123",
                "full_name": "Администратор Системы",
                "role": "admin",
                "is_active": True
            },
            {
                "email": "hr@company.com", 
                "password": "hr123",
                "full_name": "HR Менеджер",
                "role": "hr",
                "is_active": True
            },
            {
                "email": "recruiter@company.com",
                "password": "recruiter123", 
                "full_name": "Рекрутер",
                "role": "hr",
                "is_active": True
            },
            {
                "email": "manager@company.com",
                "password": "manager123",
                "full_name": "Менеджер по персоналу", 
                "role": "hr",
                "is_active": True
            }
        ]
        
        print(f"\n👤 Создание {len(test_users)} тестовых пользователей...")
        
        created_users = []
        for user_data in test_users:
            try:
                # Создаем пользователя
                user = User(
                    email=user_data["email"],
                    hashed_password=security_service.get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_active=user_data["is_active"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                await user.insert()
                created_users.append(user)
                
                print(f"✅ Создан: {user.email} (пароль: {user_data['password']})")
                
            except Exception as e:
                print(f"❌ Ошибка создания {user_data['email']}: {e}")
        
        print(f"\n🎉 Успешно создано {len(created_users)} пользователей!")
        
        # Выводим информацию для входа
        print("\n" + "=" * 50)
        print("🔑 ДАННЫЕ ДЛЯ ВХОДА В СИСТЕМУ:")
        print("=" * 50)
        
        for user_data in test_users:
            print(f"📧 Email: {user_data['email']}")
            print(f"🔒 Пароль: {user_data['password']}")
            print(f"👤 Роль: {user_data['role']}")
            print(f"📝 Имя: {user_data['full_name']}")
            print("-" * 30)
        
        print("✅ Тестовые пользователи готовы!")
        print("🌐 Теперь можно войти в систему на http://localhost:3000")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания пользователей: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    result = asyncio.run(create_test_users())
    if not result:
        sys.exit(1)