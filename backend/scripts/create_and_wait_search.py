"""Create a new search and wait for it to process"""
import asyncio
import sys
import os
import httpx
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def create_and_wait():
    """Create a search and monitor its progress"""
    
    print("=" * 80)
    print("СОЗДАНИЕ И МОНИТОРИНГ ПОИСКА")
    print("=" * 80)
    print()
    
    API_URL = "http://localhost:8000"
    
    # Login
    print("1. Авторизация...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            login_response = await client.post(
                f"{API_URL}/api/v1/auth/login",
                json={
                    "email_or_username": "admin",
                    "password": "admin123"
                }
            )
            
            if login_response.status_code != 200:
                print(f"   ❌ Ошибка авторизации: {login_response.status_code}")
                print(f"   {login_response.text[:200]}")
                return
            
            token = login_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            print("   ✅ Авторизация успешна")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return
        
        # Create search
        print()
        print("2. Создание поиска...")
        test_query = "Сварщик с опытом работы от 3 лет, знание ручной дуговой сварки"
        search_data = {
            "query": test_query,
            "city": "Москва"
        }
        
        try:
            search_response = await client.post(
                f"{API_URL}/api/v1/search",
                json=search_data,
                headers=headers
            )
            
            if search_response.status_code != 201:
                print(f"   ❌ Ошибка создания поиска: {search_response.status_code}")
                print(f"   {search_response.text[:200]}")
                return
            
            search = search_response.json()
            search_id = search["id"]
            print(f"   ✅ Поиск создан: {search_id}")
            print(f"   Статус: {search.get('status', 'unknown')}")
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return
        
        # Monitor progress
        print()
        print("3. Мониторинг обработки...")
        print("   (Проверка каждые 3 секунды, максимум 2 минуты)")
        print()
        
        max_wait = 120  # 2 minutes
        elapsed = 0
        check_interval = 3
        
        while elapsed < max_wait:
            try:
                status_response = await client.get(
                    f"{API_URL}/api/v1/search/{search_id}/status",
                    headers=headers
                )
                
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    current_status = status_data.get("status", "unknown")
                    
                    print(f"   [{elapsed:3d}s] Статус: {current_status}", end="")
                    
                    if current_status == "completed":
                        print(" ✅")
                        print()
                        print("=" * 80)
                        print("ПОИСК ЗАВЕРШЕН УСПЕШНО!")
                        print("=" * 80)
                        print(f"📋 ID: {search_id}")
                        print(f"🌐 Откройте: http://localhost:3000/results/{search_id}")
                        return
                    elif current_status == "failed":
                        print(f" ❌")
                        print(f"   Ошибка: {status_data.get('error_message', 'Unknown error')}")
                        return
                    elif current_status == "processing":
                        print(" ⏳")
                    else:
                        print()
                    
                    elapsed += check_interval
                    await asyncio.sleep(check_interval)
                else:
                    print(f"   ⚠️  Ошибка получения статуса: {status_response.status_code}")
                    elapsed += check_interval
                    await asyncio.sleep(check_interval)
            except Exception as e:
                print(f"   ⚠️  Ошибка: {e}")
                elapsed += check_interval
                await asyncio.sleep(check_interval)
        
        print()
        print("⏱️  Превышено время ожидания")
        print(f"🌐 Проверьте статус вручную: http://localhost:3000/results/{search_id}")

if __name__ == "__main__":
    asyncio.run(create_and_wait())
