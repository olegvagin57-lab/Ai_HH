"""Test HH Client with mock parser"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.hh_client import hh_client

async def test_hh_client():
    """Test HH client functionality"""
    try:
        print("Testing HH Client...")
        
        # Test search
        print("\nTesting resume search...")
        resumes = await hh_client.search_resumes(
            city="Москва",
            query="Python разработчик",
            max_resumes=10
        )
        
        print(f"Found {len(resumes)} resumes")
        
        if resumes:
            print(f"\nFirst resume:")
            first_resume = resumes[0]
            print(f"- Name: {first_resume.get('name')}")
            print(f"- Title: {first_resume.get('title')}")
            print(f"- City: {first_resume.get('city')}")
            print(f"- Experience: {first_resume.get('experience')}")
            print(f"- Skills: {', '.join(first_resume.get('skills', [])[:5])}")
        
        print("\nHH Client test completed!")
        
    except Exception as e:
        print(f"HH Client test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_hh_client())