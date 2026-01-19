"""Create search for worker professions"""
import asyncio
import sys
import os
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Test query for worker professions
TEST_QUERY = """Сварщик с опытом работы от 3 лет, знание ручной дуговой сварки, аргонодуговой сварки, сварки в защитных газах. Требуется опыт работы с черными и цветными металлами, знание чтения чертежей, опыт работы на производстве. Желательно наличие удостоверения сварщика и допуска к работам повышенной опасности."""
TEST_CITY = "Москва"

async def create_search():
    """Create search for worker professions"""
    
    print("=" * 80)
    print("СОЗДАНИЕ ПОИСКА ДЛЯ РАБОЧИХ ПРОФЕССИЙ")
    print("=" * 80)
    print()
    
    API_URL = "http://localhost:8000"
    
    # Step 1: Login
    print("1. Авторизация...")
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            login_response = await client.post(
                f"{API_URL}/api/v1/auth/login",
                data={
                    "username": "admin@example.com",
                    "password": "admin123"
                }
            )
            
            if login_response.status_code == 200:
                token = login_response.json()["access_token"]
                print("   ✅ Авторизация успешна")
            else:
                print(f"   ⚠️  Авторизация не удалась: {login_response.status_code}")
                print(f"   Ответ: {login_response.text[:200]}")
                print()
                print("   Попробуйте зарегистрироваться или использовать существующий аккаунт")
                return None
        except Exception as e:
            print(f"   ❌ Ошибка авторизации: {e}")
            return None
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 2: Create search
        print()
        print("2. Создание поиска...")
        print(f"   Запрос: {TEST_QUERY[:80]}...")
        print(f"   Город: {TEST_CITY}")
        
        search_data = {
            "query": TEST_QUERY,
            "city": TEST_CITY
        }
        
        try:
            search_response = await client.post(
                f"{API_URL}/api/v1/search",
                json=search_data,
                headers=headers
            )
            
            if search_response.status_code == 201:
                search = search_response.json()
                search_id = search["id"]
                print(f"   ✅ Поиск создан: ID = {search_id}")
                print(f"   Статус: {search.get('status', 'unknown')}")
                print()
                print("=" * 80)
                print("ПОИСК СОЗДАН УСПЕШНО!")
                print("=" * 80)
                print()
                print(f"📋 ID поиска: {search_id}")
                print(f"🌐 Откройте во фронтенде:")
                print(f"   http://localhost:3000/results/{search_id}")
                print()
                print("⏳ Поиск обрабатывается...")
                print("   Проверьте статус через несколько секунд:")
                print(f"   python scripts/check_search_status.py")
                print()
                print("💡 В логах Celery worker вы увидите:")
                print("   [INFO] Processing search")
                print("   [INFO] Concepts extracted via Ollama (GPU)")
                print("   [INFO] Resume analyzed via Ollama (GPU)")
                
                return search_id
            else:
                print(f"   ❌ Ошибка создания поиска: {search_response.status_code}")
                print(f"   Ответ: {search_response.text[:200]}")
                return None
        except Exception as e:
            print(f"   ❌ Ошибка: {e}")
            return None

if __name__ == "__main__":
    print()
    print("⚠️  Убедитесь, что:")
    print("   1. Бэкенд запущен: uvicorn app.main:app --reload --port 8000")
    print("   2. Celery worker запущен (должен быть запущен в отдельном окне)")
    print("   3. MongoDB и Redis запущены")
    print("   4. Ollama запущена и использует GPU")
    print()
    
    result = asyncio.run(create_search())
