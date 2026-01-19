"""Final comprehensive test after all fixes"""
import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def final_test():
    """Run final test"""
    print("=" * 80)
    print("ФИНАЛЬНОЕ ТЕСТИРОВАНИЕ ПОСЛЕ ИСПРАВЛЕНИЙ")
    print("=" * 80)
    print()
    
    API_URL = "http://localhost:8000"
    
    # Test 1: Auth
    print("1. Тест авторизации...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{API_URL}/api/v1/auth/login",
                json={"email_or_username": "admin@test.com", "password": "Admin123!"}
            )
            if response.status_code == 200:
                token = response.json()["access_token"]
                headers = {"Authorization": f"Bearer {token}"}
                print("   ✓ Авторизация успешна")
            else:
                print(f"   ✗ Ошибка: {response.status_code}")
                return
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            return
        
        # Test 2: Create search
        print()
        print("2. Создание поиска...")
        try:
            response = await client.post(
                f"{API_URL}/api/v1/search",
                json={"query": "Python developer", "city": "Москва"},
                headers=headers
            )
            if response.status_code == 201:
                search = response.json()
                search_id = search["id"]
                print(f"   ✓ Поиск создан: {search_id}")
                print(f"   Статус: {search.get('status')}")
            else:
                print(f"   ✗ Ошибка: {response.status_code}")
                print(f"   {response.text[:200]}")
                return
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            return
        
        # Test 3: Get status (should not return 500)
        print()
        print("3. Получение статуса...")
        try:
            response = await client.get(
                f"{API_URL}/api/v1/search/{search_id}/status",
                headers=headers
            )
            if response.status_code == 200:
                status_data = response.json()
                print(f"   ✓ Статус получен: {status_data.get('status')}")
                print(f"   Прогресс: {status_data.get('processed_count', 0)}/{status_data.get('total_to_process', 0)}")
            else:
                print(f"   ✗ Ошибка: {response.status_code}")
                print(f"   {response.text[:200]}")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
        
        # Test 4: Get search (should not return 500)
        print()
        print("4. Получение поиска...")
        try:
            response = await client.get(
                f"{API_URL}/api/v1/search/{search_id}",
                headers=headers
            )
            if response.status_code == 200:
                search_data = response.json()
                print(f"   ✓ Поиск получен: {search_data.get('status')}")
            else:
                print(f"   ✗ Ошибка: {response.status_code}")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
        
        # Test 5: Get resumes (should handle gracefully even if no resumes)
        print()
        print("5. Получение резюме...")
        try:
            response = await client.get(
                f"{API_URL}/api/v1/search/{search_id}/resumes",
                headers=headers,
                params={"page": 1, "page_size": 10}
            )
            if response.status_code == 200:
                data = response.json()
                print(f"   ✓ Резюме получены: {data.get('total', 0)}")
            else:
                print(f"   ✗ Ошибка: {response.status_code}")
                print(f"   {response.text[:300]}")
        except Exception as e:
            print(f"   ✗ Ошибка: {e}")
            import traceback
            traceback.print_exc()
    
    print()
    print("=" * 80)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("=" * 80)
    print()
    print("Если все тесты прошли успешно (✓), значит исправления работают!")
    print("Если поиск не обрабатывается автоматически, проверьте логи Celery worker'а")

if __name__ == "__main__":
    asyncio.run(final_test())
