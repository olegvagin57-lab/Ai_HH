#!/usr/bin/env python3
"""
Test script for HH Resume Analyzer system
Run this to test the basic functionality
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.ai_service import ai_service
from app.services.hh_client import hh_client
from app.services.search_service_mongo import search_service


async def test_ai_service():
    """Test AI service functionality"""
    print("[AI] Testing AI Service...")
    
    # Test concept extraction
    query = "Нужен активный менеджер по продажам спецодежды B2B"
    concepts = await ai_service.extract_concepts(query)
    print(f"[OK] Concepts extracted: {concepts}")
    
    # Test resume analysis
    mock_resume = {
        "title": "Менеджер по продажам",
        "experience": [
            {
                "position": "Менеджер по продажам",
                "company": "ООО Рога и копыта",
                "description": "Продажи спецодежды корпоративным клиентам"
            }
        ],
        "skills": "Продажи B2B, работа с тендерами"
    }
    
    analysis = await ai_service.analyze_resume(
        mock_resume, query, concepts
    )
    
    score = analysis.get("score")
    summary = analysis.get("summary")
    questions = analysis.get("questions")
    ai_generated = analysis.get("ai_generated")
    
    print("Resume analyzed:")
    print(f"   Score: {score}/10")
    print(f"   Summary: {summary}")
    print(f"   Questions: {questions}")
    print(f"   AI Generated: {ai_generated}")


async def test_hh_client():
    """Test HH client functionality"""
    print("\n[HH] Testing HH Client...")
    
    resumes = await hh_client.search_resumes("Москва", "менеджер по продажам", 5)
    print(f"[OK] Found {len(resumes)} resumes")
    
    if resumes:
        details = await hh_client.get_resume_details(resumes[0]["hh_id"])
        print(f"[OK] Resume details fetched: {bool(details)}")


async def test_integration():
    """Test full integration"""
    print("\n[INTEGRATION] Testing Full Integration...")
    
    # This would normally be done through the API
    # but we can test the service directly
    print("Integration test would require database setup")
    print("   Run with Docker Compose for full integration test")


async def main():
    """Run all tests"""
    print("Starting HH Resume Analyzer Tests\n")
    
    try:
        await test_ai_service()
        await test_hh_client()
        await test_integration()
        
        print("\nAll tests completed successfully!")
        print("\nNext steps:")
        print("1. Get HH API keys and add to backend/.env")
        print("2. Get Gemini API key and add to backend/.env")
        print("3. Run: docker-compose up --build")
        print("4. Open: http://localhost:3000")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)