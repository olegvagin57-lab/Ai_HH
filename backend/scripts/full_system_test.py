"""Full system test from A to Z"""
import asyncio
import sys
import os
import httpx
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"[OK] {msg}")

def print_error(msg):
    print(f"[ERROR] {msg}")

def print_warning(msg):
    print(f"[WARN] {msg}")

def print_info(msg):
    print(f"[INFO] {msg}")

async def test_services():
    """Test 1: Check all services"""
    print("\n" + "="*80)
    print("ТЕСТ 1: ПРОВЕРКА СЕРВИСОВ")
    print("="*80)
    
    results = {}
    
    # MongoDB
    try:
        from app.infrastructure.database.mongodb import connect_to_mongo
        await connect_to_mongo()
        print_success("MongoDB: подключен")
        results['mongodb'] = True
    except Exception as e:
        print_error(f"MongoDB: ошибка - {e}")
        results['mongodb'] = False
    
    # Redis
    try:
        import redis
        r = redis.Redis.from_url('redis://localhost:6379', decode_responses=True)
        r.ping()
        print_success("Redis: подключен")
        results['redis'] = True
    except Exception as e:
        print_error(f"Redis: ошибка - {e}")
        results['redis'] = False
    
    # Backend API
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:8000/api/v1/health")
            if response.status_code == 200:
                print_success("Backend API: работает")
                results['backend'] = True
            else:
                print_error(f"Backend API: статус {response.status_code}")
                results['backend'] = False
    except Exception as e:
        print_error(f"Backend API: ошибка - {e}")
        results['backend'] = False
    
    # Ollama
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11434/api/tags")
            if response.status_code == 200:
                print_success("Ollama: работает")
                results['ollama'] = True
            else:
                print_warning(f"Ollama: статус {response.status_code}")
                results['ollama'] = False
    except Exception as e:
        print_warning(f"Ollama: недоступна - {e}")
        results['ollama'] = False
    
    # Celery
    try:
        from celery_app.celery import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            print_success(f"Celery: {len(stats)} worker(ов) активны")
            results['celery'] = True
        else:
            print_warning("Celery: нет активных worker'ов")
            results['celery'] = False
    except Exception as e:
        print_warning(f"Celery: ошибка - {e}")
        results['celery'] = False
    
    return results

async def test_auth():
    """Test 2: Authentication"""
    print("\n" + "="*80)
    print("ТЕСТ 2: АВТОРИЗАЦИЯ")
    print("="*80)
    
    API_URL = "http://localhost:8000"
    token = None
    client = None
    
    # Check users in DB
    try:
        from app.infrastructure.database.mongodb import connect_to_mongo
        from app.domain.entities.user import User
        await connect_to_mongo()
        users = await User.find_all().to_list()
        print_info(f"Пользователей в базе: {len(users)}")
        if users:
            for u in users[:3]:
                print_info(f"  - {u.email} ({u.username})")
    except Exception as e:
        print_warning(f"Не удалось проверить пользователей: {e}")
    
    # Try login - create client here and keep it open
    client = httpx.AsyncClient(timeout=30.0)
    credentials = [
        {"email_or_username": "admin@test.com", "password": "Admin123!"},
        {"email_or_username": "admin", "password": "Admin123!"},
        {"email_or_username": "hr@test.com", "password": "Hr123456!"},
    ]
    
    for creds in credentials:
        try:
            response = await client.post(
                f"{API_URL}/api/v1/auth/login",
                json=creds
            )
            if response.status_code == 200:
                data = response.json()
                token = data["access_token"]
                user = data.get("user", {})
                print_success(f"Авторизация успешна: {user.get('username', 'N/A')}")
                return token, client
            else:
                print_warning(f"Не удалось: {creds['email_or_username']} - {response.status_code}")
        except Exception as e:
            print_warning(f"Ошибка авторизации: {e}")
    
    if not token:
        print_error("Не удалось авторизоваться")
        if client:
            await client.aclose()
        return None, None
    
    return token, client

async def test_create_search(token, client):
    """Test 3: Create search"""
    print("\n" + "="*80)
    print("ТЕСТ 3: СОЗДАНИЕ ПОИСКА")
    print("="*80)
    
    API_URL = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    search_data = {
        "query": "Сварщик с опытом работы от 3 лет, знание ручной дуговой сварки, аргонодуговой сварки",
        "city": "Москва"
    }
    
    try:
        response = await client.post(
            f"{API_URL}/api/v1/search",
            json=search_data,
            headers=headers
        )
        
        if response.status_code == 201:
            search = response.json()
            search_id = search["id"]
            print_success(f"Поиск создан: {search_id}")
            print_info(f"Статус: {search.get('status', 'unknown')}")
            return search_id
        else:
            print_error(f"Ошибка создания поиска: {response.status_code}")
            print_error(f"Ответ: {response.text[:200]}")
            return None
    except Exception as e:
        print_error(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return None

async def test_search_processing(search_id, token, client):
    """Test 4: Monitor search processing"""
    print("\n" + "="*80)
    print("ТЕСТ 4: ОБРАБОТКА ПОИСКА")
    print("="*80)
    
    API_URL = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    max_wait = 60  # 1 minute
    elapsed = 0
    check_interval = 3
    
    print_info("Мониторинг обработки (максимум 60 секунд)...")
    
    while elapsed < max_wait:
        try:
            response = await client.get(
                f"{API_URL}/api/v1/search/{search_id}/status",
                headers=headers
            )
            
            if response.status_code == 200:
                status_data = response.json()
                current_status = status_data.get("status", "unknown")
                
                print_info(f"[{elapsed:3d}s] Статус: {current_status}")
                
                if current_status == "completed":
                    print_success("Поиск завершен!")
                    return True
                elif current_status == "failed":
                    error_msg = status_data.get("error_message", "Unknown error")
                    print_error(f"Поиск завершился с ошибкой: {error_msg}")
                    return False
                elif current_status == "processing":
                    print_info("Поиск обрабатывается...")
                
                elapsed += check_interval
                await asyncio.sleep(check_interval)
            else:
                print_warning(f"Ошибка получения статуса: {response.status_code}")
                elapsed += check_interval
                await asyncio.sleep(check_interval)
        except Exception as e:
            print_warning(f"Ошибка: {e}")
            elapsed += check_interval
            await asyncio.sleep(check_interval)
    
    print_warning("Превышено время ожидания")
    return False

async def test_get_results(search_id, token, client):
    """Test 5: Get search results"""
    print("\n" + "="*80)
    print("ТЕСТ 5: ПОЛУЧЕНИЕ РЕЗУЛЬТАТОВ")
    print("="*80)
    
    API_URL = "http://localhost:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = await client.get(
            f"{API_URL}/api/v1/search/{search_id}/resumes",
            headers=headers,
            params={"page": 1, "page_size": 10}
        )
        
        if response.status_code == 200:
            data = response.json()
            resumes = data.get("items", [])
            total = data.get("total", 0)
            
            print_success(f"Найдено резюме: {total}")
            
            if resumes:
                print_info("Топ-3 резюме:")
                for i, resume in enumerate(resumes[:3], 1):
                    name = resume.get("name", "N/A")
                    score = resume.get("ai_score", "N/A")
                    hh_url = resume.get("hh_url", "N/A")
                    print_info(f"  {i}. {name} - Оценка: {score}")
                    if hh_url and hh_url != "N/A":
                        print_info(f"     Ссылка: {hh_url}")
                return True
            else:
                print_warning("Резюме не найдены")
                return False
        else:
            print_error(f"Ошибка получения результатов: {response.status_code}")
            print_error(f"Ответ: {response.text[:200]}")
            return False
    except Exception as e:
        print_error(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("ПОЛНОЕ ТЕСТИРОВАНИЕ СИСТЕМЫ")
    print("="*80)
    
    # Test 1: Services
    services = await test_services()
    if not all([services.get('mongodb'), services.get('redis'), services.get('backend')]):
        print_error("\nКритические сервисы не работают! Исправьте их перед продолжением.")
        return
    
    # Test 2: Auth
    token, client = await test_auth()
    if not token:
        print_error("\nНе удалось авторизоваться! Проверьте пользователей в базе.")
        if client:
            await client.aclose()
        return
    
    # Test 3: Create search
    search_id = await test_create_search(token, client)
    if not search_id:
        print_error("\nНе удалось создать поиск!")
        return
    
    # Test 4: Processing
    processed = await test_search_processing(search_id, token, client)
    if not processed:
        print_warning("\nПоиск не завершился за отведенное время")
        print_info(f"Проверьте вручную: http://localhost:3000/results/{search_id}")
    
    # Test 5: Results
    if processed:
        await test_get_results(search_id, token, client)
    
    # Summary
    print("\n" + "="*80)
    print("ИТОГИ ТЕСТИРОВАНИЯ")
    print("="*80)
    print_info(f"Поиск ID: {search_id}")
    print_info(f"Фронтенд: http://localhost:3000/results/{search_id}")
    
    if processed:
        print_success("\nВсе тесты пройдены успешно!")
    else:
        print_warning("\nНекоторые тесты не завершились. Проверьте логи Celery worker.")
    
    # Close client
    if client:
        await client.aclose()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nТестирование прервано пользователем")
    except Exception as e:
        print_error(f"\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()
