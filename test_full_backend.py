#!/usr/bin/env python3
"""
Тест запуска полного backend для функционального тестирования
"""

import sys
import os
sys.path.append('backend')

def test_imports():
    """Тестирование импортов"""
    print("🔍 Проверка импортов...")
    
    try:
        from app.main import app
        print("✅ app.main импортирован успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка импорта app.main: {e}")
        return False

def test_config():
    """Тестирование конфигурации"""
    print("🔍 Проверка конфигурации...")
    
    try:
        from app.core.config import settings
        print(f"✅ Конфигурация загружена")
        print(f"   MongoDB URL: {settings.mongodb_url}")
        print(f"   Debug: {settings.debug}")
        return True
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_database():
    """Тестирование подключения к базе данных"""
    print("🔍 Проверка подключения к MongoDB...")
    
    try:
        from app.database.mongodb import mongodb
        print("✅ MongoDB модуль импортирован")
        return True
    except Exception as e:
        print(f"❌ Ошибка MongoDB: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование полного backend...")
    print("=" * 50)
    
    tests = [
        ("Импорты", test_imports),
        ("Конфигурация", test_config),
        ("База данных", test_database)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Тест: {test_name}")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены! Можно запускать полный backend")
        return True
    else:
        print("❌ Есть проблемы, нужно исправить перед запуском")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)