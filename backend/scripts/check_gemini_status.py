"""Check Gemini API status via Cloudflare Worker"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx
from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def check_cloudflare_worker():
    """Check Cloudflare Worker status and test endpoints"""
    print("=" * 80)
    print("Проверка статуса Cloudflare Worker (Gemini API)")
    print("=" * 80)
    print()
    
    worker_url = settings.cloudflare_worker_url
    print(f"🌐 URL Cloudflare Worker: {worker_url}")
    print()
    
    # Test 1: Basic connectivity
    print("📡 Тест 1: Проверка доступности Worker...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(worker_url)
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            print()
    except httpx.TimeoutException:
        print("   ❌ Timeout - Worker не отвечает")
        print()
    except Exception as e:
        print(f"   ❌ Ошибка: {str(e)}")
        print()
    
    # Test 2: Extract concepts endpoint
    print("🧠 Тест 2: Проверка endpoint extract_concepts...")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{worker_url}/extract_concepts",
                json={"query": "Python разработчик"},
                timeout=10.0
            )
            print(f"   Status Code: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            print(f"   Response: {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   ✅ Успешно! Концепты: {data.get('concepts', [])[:3]}")
                except:
                    print(f"   ⚠️  Ответ не в формате JSON")
            elif response.status_code == 404:
                print(f"   ❌ 404 - Endpoint не найден. Возможно, Worker не развернут или URL неверный")
            elif response.status_code == 429:
                print(f"   ⚠️  429 - Rate limit превышен (слишком много запросов)")
            elif response.status_code == 500:
                print(f"   ❌ 500 - Ошибка сервера. Возможно, проблема с Gemini API")
            elif response.status_code == 503:
                print(f"   ⚠️  503 - Сервис недоступен. Возможно, закончилась квота Gemini API")
            else:
                print(f"   ⚠️  Неожиданный статус: {response.status_code}")
            print()
    except httpx.TimeoutException:
        print("   ❌ Timeout - Worker не отвечает")
        print()
    except Exception as e:
        print(f"   ❌ Ошибка: {str(e)}")
        print()
    
    # Test 3: Analyze resume endpoint
    print("🤖 Тест 3: Проверка endpoint analyze_resume...")
    try:
        test_resume_text = """
        Должность: Python Developer
        Имя: Иван Иванов
        Возраст: 30
        Город: Москва
        Навыки: Python, FastAPI, MongoDB, Docker
        Опыт: 5 лет разработки на Python
        """
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{worker_url}/analyze_resume",
                json={
                    "resume_text": test_resume_text,
                    "concepts": [["python", "python"], ["разработчик", "developer"]]
                },
                timeout=30.0
            )
            print(f"   Status Code: {response.status_code}")
            print(f"   Response: {response.text[:500]}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    score = data.get("score", "N/A")
                    print(f"   ✅ Успешно! Оценка: {score}/10")
                except:
                    print(f"   ⚠️  Ответ не в формате JSON")
            elif response.status_code == 404:
                print(f"   ❌ 404 - Endpoint не найден")
            elif response.status_code == 429:
                print(f"   ⚠️  429 - Rate limit превышен")
            elif response.status_code == 500:
                print(f"   ❌ 500 - Ошибка сервера")
            elif response.status_code == 503:
                print(f"   ⚠️  503 - Сервис недоступен. Возможно, закончилась квота Gemini API")
            else:
                print(f"   ⚠️  Неожиданный статус: {response.status_code}")
            print()
    except httpx.TimeoutException:
        print("   ❌ Timeout - Worker не отвечает (возможно, долгая обработка)")
        print()
    except Exception as e:
        print(f"   ❌ Ошибка: {str(e)}")
        print()
    
    # Summary
    print("=" * 80)
    print("📋 РЕКОМЕНДАЦИИ:")
    print("=" * 80)
    print()
    print("Если вы видите ошибки 429 или 503:")
    print("  1. Проверьте квоту Gemini API в Google Cloud Console")
    print("  2. Возможно, закончился бесплатный лимит (60 запросов/минуту)")
    print("  3. Проверьте, не превышен ли дневной лимит")
    print()
    print("Если вы видите ошибку 404:")
    print("  1. Проверьте, что Cloudflare Worker развернут")
    print("  2. Проверьте правильность URL в настройках")
    print()
    print("Если Worker недоступен:")
    print("  1. Система автоматически переключится на fallback режим")
    print("  2. Fallback режим работает без Gemini API, но с базовым анализом")
    print()
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(check_cloudflare_worker())
