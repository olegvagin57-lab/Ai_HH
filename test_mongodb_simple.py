"""Simple MongoDB connection test"""
import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.models.user_mongo import User
from app.services.user_service_mongo import user_service


async def test_mongodb_simple():
    """Simple MongoDB connection test"""
    try:
        print("Connecting to MongoDB...")
        await connect_to_mongo()
        print("MongoDB connection successful!")
        
        # Test creating a user
        print("\nTesting user creation...")
        
        # Initialize roles and permissions
        await user_service.initialize_default_roles_and_permissions()
        print("✅ Default roles and permissions initialized")
        
        # Create test user
        test_user = await user_service.create_user(
            email="test@example.com",
            username="testuser",
            password="TestPass123!",
            full_name="Test User"
        )
        
        if test_user:
            print(f"Test user created: {test_user.email}")
            
            # Clean up - delete test user
            await test_user.delete()
            print("Test user cleaned up")
        else:
            print("User creation failed")
        
        print("\nAll MongoDB tests passed!")
        
    except Exception as e:
        print(f"MongoDB test failed: {e}")
    finally:
        await close_mongo_connection()
        print("MongoDB connection closed")


if __name__ == "__main__":
    asyncio.run(test_mongodb_simple())