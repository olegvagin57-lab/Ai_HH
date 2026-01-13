#!/usr/bin/env python3
"""Fix MongoDB indexes - remove conflicting indexes"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings

async def fix_indexes():
    """Remove conflicting indexes"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_database]
    
    print("Connecting to MongoDB...")
    
    # Get resumes collection
    resumes_collection = db.resumes
    
    # List existing indexes
    print("\nExisting indexes on 'resumes' collection:")
    indexes = await resumes_collection.list_indexes().to_list(length=100)
    for idx in indexes:
        print(f"  - {idx.get('name')}: {idx.get('key')} (unique: {idx.get('unique', False)})")
    
    # Check for conflicting hh_id index
    hh_id_index = None
    for idx in indexes:
        if idx.get('name') == 'hh_id_1':
            hh_id_index = idx
            break
    
    if hh_id_index:
        print(f"\nFound hh_id_1 index: {hh_id_index}")
        print("Dropping old hh_id_1 index to recreate with correct definition...")
        try:
            await resumes_collection.drop_index('hh_id_1')
            print("[OK] Old index dropped successfully")
        except Exception as e:
            print(f"[WARN] Error dropping index: {e}")
            print("Trying to drop by key pattern...")
            try:
                # Try dropping by key pattern
                await resumes_collection.drop_index([("hh_id", 1)])
                print("[OK] Index dropped by key pattern")
            except Exception as e2:
                print(f"[WARN] Could not drop index: {e2}")
                print("Index may need to be dropped manually or will be recreated on next startup")
    
    print("\n[OK] Index fix completed. Restart backend to recreate indexes.")
    client.close()

if __name__ == "__main__":
    asyncio.run(fix_indexes())
