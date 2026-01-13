#!/usr/bin/env python3
"""
Test updated Cloudflare Worker integration
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_service import ai_service
from app.core.logging import logger


async def test_ai_service_integration():
    """Test AI service with fallback logic"""
    print("Testing AI Service integration...")
    
    test_query = "Python разработчик Django"
    
    try:
        # Test concept extraction (should fallback to mock if Cloudflare unavailable)
        print(f"\n1. Testing concept extraction for: '{test_query}'")
        concepts = await ai_service.extract_concepts(test_query)
        print(f"Concepts extracted: {concepts}")
        
        # Test resume analysis (should fallback to mock if Cloudflare unavailable)
        print(f"\n2. Testing resume analysis...")
        test_resume = {
            "name": "Алексей Иванов",
            "age": 25,
            "title": "Python Developer",
            "experience": [
                {
                    "position": "Python Developer",
                    "company": "IT Company",
                    "start": "2021-01-01",
                    "end": "2024-01-01",
                    "description": "Разработка веб-приложений на Django и FastAPI"
                }
            ],
            "skills": "Python, Django, FastAPI, PostgreSQL, Redis",
            "education": [
                {
                    "name": "Технический университет",
                    "year": 2020,
                    "organization": "Факультет информатики"
                }
            ]
        }
        
        analysis = await ai_service.analyze_resume(
            test_resume, test_query, concepts
        )
        
        print("Resume analysis completed:")
        print(f"   Score: {analysis.get('score')}/10")
        print(f"   Summary: {analysis.get('summary')}")
        print(f"   Questions: {len(analysis.get('questions') or [])} questions generated")
        print(f"   AI Generated: {analysis.get('ai_generated')}")
        
        print("\nAI Service integration test completed successfully!")
        print("   Note: If Cloudflare Worker is unavailable, fallback logic was used")
        
    except Exception as e:
        print(f"Test failed: {e}")
        logger.error(f"AI service integration test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    print("Starting AI Service integration test...")
    
    # Run test
    success = asyncio.run(test_ai_service_integration())
    
    if success:
        print("\nTest completed successfully!")
        print("\nNext steps:")
        print("1. Set up Cloudflare Worker with proper endpoints:")
        print("   - POST /extract-concepts")
        print("   - POST /analyze-resume")
        print("2. Test with real Cloudflare Worker once it's deployed")
        sys.exit(0)
    else:
        print("\nTest failed!")
        sys.exit(1)