"""Quick test of Cloudflare Worker"""
import asyncio
import httpx

async def test():
    url = "https://proud-water-5293.olegvagin1311.workers.dev/extract_concepts"
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            r = await client.post(url, json={"query": "Python разработчик"})
            print(f"Status: {r.status_code}")
            print(f"Response: {r.text[:500]}")
            if r.status_code == 200:
                print("✅ Worker работает!")
            else:
                print("❌ Worker вернул ошибку")
        except Exception as e:
            print(f"❌ Ошибка: {e}")

asyncio.run(test())
