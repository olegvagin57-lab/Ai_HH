"""Script to create test users for development"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.database.mongodb import connect_to_mongo
from app.application.services.auth_service import AuthService

configure_logging()
logger = get_logger(__name__)


async def create_test_users():
    """Create test users"""
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
            from app.domain.entities.user import User
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
    
    print(f"\n✅ Created {created_count} user(s)")
    if skipped_count > 0:
        print(f"⏭️  Skipped {skipped_count} user(s) (already exist)")
    
    return created_count, skipped_count


async def main():
    """Main function"""
    print("=" * 60)
    print("Create Test Users")
    print("=" * 60)
    print(f"Database: {settings.mongodb_database}")
    print(f"MongoDB URL: {settings.mongodb_url}")
    print()
    
    try:
        created, skipped = await create_test_users()
        print()
        print("✅ Test users setup completed!")
        print()
        print("Test users:")
        print("  - admin@test.com / Admin123! (admin role)")
        print("  - hr@test.com / Hr123456! (hr_specialist role)")
        return 0
    except Exception as e:
        logger.error("Error creating test users", error=str(e))
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
