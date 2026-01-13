#!/usr/bin/env python3
"""
Simple test for Cloudflare Worker
"""
import asyncio
import httpx


async def test_cloudflare_worker():
    """Test Cloudflare Worker directly"""
    worker_url = "https://proud-water-5293.olegvagin1311.workers.dev"
    
    print(f"🧪 Testing Cloudflare Worker at: {worker_url}")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Test concept extraction
            print("\n1. Testing concept extraction...")
            response = await client.post(
                f"{worker_url}/extract-concepts",
                json={"query": "Менеджер по продажам B2B"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Concept extraction successful: {data}")
            else:
                print(f"❌ Concept extraction failed: {response.status_code} - {response.text}")
                return False
            
            # Test resume analysis
            print("\n2. Testing resume analysis...")
            test_resume = {
                "title": "Менеджер по продажам",
                "skills": "Продажи B2B, работа с клиентами"
            }
            
            response = await client.post(
                f"{worker_url}/analyze-resume",
                json={
                    "resume_data": test_resume,
                    "query": "Менеджер по продажам B2B",
                    "concepts": [["продажи", "sales"], ["b2b", "корпоративные"]]
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Resume analysis successful: {data}")
            else:
                print(f"❌ Resume analysis failed: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False
    
    print(f"\n🎉 Cloudflare Worker test completed successfully!")
    return True


if __name__ == "__main__":
    success = asyncio.run(test_cloudflare_worker())
    if success:
        print("✅ All tests passed!")
    else:
        print("❌ Tests failed!")