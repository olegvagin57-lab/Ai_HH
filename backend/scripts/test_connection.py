"""Script to test database and external service connections"""
import asyncio
import sys
from app.config import settings
from app.core.logging import get_logger, configure_logging

configure_logging()
logger = get_logger(__name__)


async def test_mongodb():
    """Test MongoDB connection"""
    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        
        client = AsyncIOMotorClient(
            settings.mongodb_url,
            serverSelectionTimeoutMS=5000
        )
        await client.admin.command('ping')
        client.close()
        print("[OK] MongoDB connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] MongoDB connection failed: {e}")
        return False


async def test_redis():
    """Test Redis connection"""
    try:
        import redis.asyncio as redis
        
        client = redis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        await client.close()
        print("[OK] Redis connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] Redis connection failed: {e}")
        print("  (Redis is optional for rate limiting)")
        return False


async def test_cloudflare_worker():
    """Test Cloudflare Worker connection"""
    try:
        from app.infrastructure.external.cloudflare_client import cloudflare_client
        
        # Test with a simple query
        concepts = await cloudflare_client.extract_concepts("test query")
        print(f"[OK] Cloudflare Worker connection successful (got {len(concepts)} concepts)")
        return True
    except Exception as e:
        print(f"[FAIL] Cloudflare Worker connection failed: {e}")
        print("  (Will use fallback mode)")
        return False


async def main():
    """Run all connection tests"""
    print("Testing connections...")
    print("-" * 50)
    
    results = []
    results.append(await test_mongodb())
    results.append(await test_redis())
    results.append(await test_cloudflare_worker())
    
    print("-" * 50)
    
    if results[0]:  # MongoDB is required
        print("[OK] Core services are ready!")
        return 0
    else:
        print("[FAIL] MongoDB connection failed. Please check your configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
