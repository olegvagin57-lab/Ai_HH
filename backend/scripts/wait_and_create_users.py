#!/usr/bin/env python3
"""Script to wait for backend and create test users"""
import sys
import time
import urllib.request
import urllib.error
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def wait_for_backend(max_attempts=60, delay=2):
    """Wait for backend to be ready"""
    print("Waiting for backend to be ready...")
    
    for attempt in range(1, max_attempts + 1):
        try:
            req = urllib.request.Request('http://localhost:8000/api/v1/health/ready')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print("✅ Backend is ready!")
                    return True
        except (urllib.error.URLError, OSError) as e:
            print(f"Attempt {attempt}/{max_attempts}: Backend not ready yet ({e}), waiting...")
            if attempt < max_attempts:
                time.sleep(delay)
            else:
                print(f"❌ Error: Backend not ready after {max_attempts} attempts")
                return False
    
    return False

def main():
    """Main function"""
    if not wait_for_backend():
        sys.exit(1)
    
    # Import and run create_test_users
    print("Creating test users...")
    try:
        from scripts.create_test_users import create_test_users
        import asyncio
        from app.infrastructure.database.mongodb import connect_to_mongo
        
        async def run():
            await connect_to_mongo()
            await create_test_users()
        
        asyncio.run(run())
        print("✅ Test users setup completed!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error creating test users: {e}")
        # Don't fail if users already exist
        if "already exists" in str(e).lower():
            print("⚠️  Users already exist, continuing...")
            sys.exit(0)
        sys.exit(1)

if __name__ == "__main__":
    main()
