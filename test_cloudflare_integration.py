#!/usr/bin/env python3
"""
Test script for Cloudflare Worker integration
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.cloudflare_client import cloudflare_client
from app.services.ai_service import ai_service
from app.core.logging import logger


async def test_cloudflare_integration():
    """Test Cloudflare Worker integration"""
    print("🧪 Testing Cloudflare Worker integration...")
    
    # Test query
    test_query = "Менеджер по продажам B2B спецодежды"
    
    try:
        # Test concept extraction
        print(f"\n1. Testing concept extraction for: '{test_query}'")
        concepts = await ai_service.extract_concepts(test_query)
        print(f"✅ Concepts extracted: {concepts}")
        
        # Test resume analysis
        print(f"\n2. Testing resume analysis...")
        test_resume = {
            "name": "Иван Петров",
            "age": 28,
            "title": "Менеджер по продажам",
            "experience": [
                {
                    "position": "Менеджер по продажам",
                    "company": "ООО Рога и копыта",
                    "start": "2020-01-01",
                    "end": "2023-01-01",
                    "description": "Продажи спецодежды корпоративным клиентам B2B"
                }
            ],
            "skills": "Продажи B2B, работа с тендерами, знание 44-ФЗ",
            "education": [
                {
                    "name": "МГУ",
                    "year": 2018,
                    "organization": "Экономический факультет"
                }
            ]
        }
        
        score, summary, questions, ai_generated = await ai_service.analyze_resume(
            test_resume, test_query, concepts
        )
        
        print(f"✅ Resume analysis completed:")
        print(f"   Score: {score}/10")
        print(f"   Summary: {summary}")
        print(f"   Questions: {questions}")
        print(f"   AI Generated: {ai_generated}")
        
        print(f"\n🎉 Cloudflare Worker integration test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        logger.error(f"Cloudflare integration test failed: {e}")
        return False
    
    return True


async def test_direct_cloudflare_client():
    """Test direct Cloudflare client calls"""
    print("\n🔧 Testing direct Cloudflare client...")
    
    try:
        # Test concept extraction
        concepts = await cloudflare_client.extract_concepts("Python разработчик")
        print(f"✅ Direct concept extraction: {concepts}")
        
        # Test resume analysis
        test_resume = {"title": "Python Developer", "skills": "Python, Django, FastAPI"}
        score, summary, questions, ai_generated = await cloudflare_client.analyze_resume(
            test_resume, "Python разработчик", concepts
        )
        print(f"✅ Direct resume analysis: score={score}, summary='{summary[:50]}...'")
        
    except Exception as e:
        print(f"❌ Direct client test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("🚀 Starting Cloudflare Worker integration tests...")
    
    # Run tests
    loop = asyncio.get_event_loop()
    
    # Test AI service (with fallback logic)
    success1 = loop.run_until_complete(test_cloudflare_integration())
    
    # Test direct client
    success2 = loop.run_until_complete(test_direct_cloudflare_client())
    
    if success1 and success2:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)