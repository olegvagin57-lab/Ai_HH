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
            req = urllib.request.Request('http://127.0.0.1:8000/api/v1/health/ready')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    print("[OK] Backend is ready!")
                    return True
        except (urllib.error.URLError, OSError) as e:
            print(f"Attempt {attempt}/{max_attempts}: Backend not ready yet ({e}), waiting...")
            if attempt < max_attempts:
                time.sleep(delay)
            else:
                print(f"[ERROR] Backend not ready after {max_attempts} attempts")
                return False
    
    return False

def main():
    """Main function"""
    if not wait_for_backend():
        sys.exit(1)
    
    # Import and run create_test_users
    print("Creating test users...")
    try:
        import asyncio
        from app.config import settings
        from app.core.logging import configure_logging, get_logger
        from app.infrastructure.database.mongodb import connect_to_mongo
        from app.application.services.auth_service import AuthService
        from app.domain.entities.user import User
        
        configure_logging()
        logger = get_logger(__name__)
        
        async def run():
            # Connect to MongoDB (this also initializes Beanie)
            await connect_to_mongo()
            
            # Initialize auth service
            auth_service = AuthService()
            
            # Initialize roles and permissions first
            await auth_service.initialize_default_roles_and_permissions()
            logger.info("Roles and permissions initialized")
            
            # Test users to create
            test_users = [
                {
                    "email": "admin@test.com",
                    "username": "admin",
                    "password": "Admin123!",
                    "full_name": "Admin User",
                    "role_names": ["admin"]
                },
                {
                    "email": "hr@test.com",
                    "username": "hr",
                    "password": "Hr123456!",
                    "full_name": "HR Specialist",
                    "role_names": ["hr_specialist"]
                }
            ]
            
            created_count = 0
            skipped_count = 0
            
            for user_data in test_users:
                try:
                    # Check if user already exists
                    existing = await User.find_one({"email": user_data["email"]})
                    
                    if existing:
                        logger.info(f"User {user_data['email']} already exists, skipping")
                        skipped_count += 1
                        continue
                    
                    # Create user
                    user = await auth_service.register_user(
                        email=user_data["email"],
                        username=user_data["username"],
                        password=user_data["password"],
                        full_name=user_data["full_name"],
                        role_names=user_data["role_names"]
                    )
                    
                    logger.info(f"Created user: {user_data['email']} with role(s): {user_data['role_names']}")
                    created_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating user {user_data['email']}: {e}")
                    # Don't fail if users already exist
                    if "already exists" in str(e).lower():
                        skipped_count += 1
                        continue
                    raise
            
            print(f"\n[OK] Created {created_count} user(s)")
            if skipped_count > 0:
                print(f"[SKIP] Skipped {skipped_count} user(s) (already exist)")
        
        asyncio.run(run())
        print("[OK] Test users setup completed!")
        sys.exit(0)
    except Exception as e:
        print(f"[ERROR] Error creating test users: {e}")
        import traceback
        traceback.print_exc()
        # Don't fail if users already exist
        if "already exists" in str(e).lower():
            print("[WARN] Users already exist, continuing...")
            sys.exit(0)
        sys.exit(1)

if __name__ == "__main__":
    main()
