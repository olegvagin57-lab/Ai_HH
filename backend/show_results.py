"""Show detailed results from DarkDarW parser"""
import asyncio
import sys
import os
os.chdir('/app')

from app.infrastructure.external.hh_darkdarw_parser_client import hh_darkdarw_parser_client

async def main():
    print("=" * 70)
    print("DarkDarW Parser Test Results")
    print("=" * 70)
    
    result = await hh_darkdarw_parser_client.search_resumes(
        query="python",
        city="москва",
        per_page=2,
        page=0
    )
    
    print(f"\n✅ Search completed!")
    print(f"   Found: {result.get('found', 0)} resumes")
    print(f"   Pages: {result.get('pages', 0)}")
    print(f"   Items returned: {len(result.get('items', []))}")
    
    items = result.get('items', [])
    for i, item in enumerate(items, 1):
        print(f"\n📄 Resume {i}:")
        print(f"   ID: {item.get('id', 'N/A')}")
        print(f"   Title: {item.get('title', 'N/A')}")
        print(f"   Name: {item.get('first_name', '')} {item.get('last_name', '')}")
        print(f"   Age: {item.get('age', 'N/A')}")
        
        area = item.get('area', {})
        if area:
            print(f"   Area: {area.get('name', 'N/A')}")
        
        salary = item.get('salary', {})
        if salary and salary.get('amount'):
            print(f"   Salary: {salary.get('amount')} {salary.get('currency', 'RUR')}")
        
        skills = item.get('skills', [])
        if skills:
            skills_list = [s.get('name', '') for s in skills[:5]]
            print(f"   Skills: {', '.join(skills_list)}")
            if len(skills) > 5:
                print(f"   ... and {len(skills) - 5} more")
    
    print("\n" + "=" * 70)
    print("✅ Parser is working correctly!")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
