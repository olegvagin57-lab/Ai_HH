"""Check if backend is running"""
import httpx
import asyncio

async def check():
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get('http://localhost:8000/api/v1/health')
            if r.status_code == 200:
                print("✅ Backend is running")
                return True
            else:
                print(f"⚠️  Backend returned status {r.status_code}")
                return False
    except Exception as e:
        print(f"❌ Backend is NOT running: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(check())
