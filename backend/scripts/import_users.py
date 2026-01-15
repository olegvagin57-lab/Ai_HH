"""Script to import users from JSON file to MongoDB"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.infrastructure.database.mongodb import connect_to_mongo, init_beanie
from app.domain.entities.user import User, Role, Permission

configure_logging()
logger = get_logger(__name__)


async def import_users(input_file: str, skip_existing: bool = True):
    """Import users, roles, and permissions from JSON file"""
    # Connect to MongoDB
    await connect_to_mongo()
    await init_beanie()
    
    # Read export file
    input_path = Path(input_file)
    if not input_path.exists():
        raise FileNotFoundError(f"Export file not found: {input_path}")
    
    with open(input_path, "r", encoding="utf-8") as f:
        export_data = json.load(f)
    
    logger.info(f"Importing from export created at: {export_data.get('exported_at', 'unknown')}")
    
    imported_users = 0
    skipped_users = 0
    imported_roles = 0
    skipped_roles = 0
    imported_permissions = 0
    skipped_permissions = 0
    
    # Import permissions first
    if "permissions" in export_data:
        for perm_data in export_data["permissions"]:
            existing = await Permission.find_one({"name": perm_data["name"]})
            if existing:
                if not skip_existing:
                    existing.description = perm_data.get("description", existing.description)
                    await existing.save()
                    imported_permissions += 1
                else:
                    skipped_permissions += 1
            else:
                permission = Permission(
                    name=perm_data["name"],
                    description=perm_data.get("description", "")
                )
                await permission.insert()
                imported_permissions += 1
                logger.info(f"Imported permission: {perm_data['name']}")
    
    # Import roles
    if "roles" in export_data:
        for role_data in export_data["roles"]:
            existing = await Role.find_one({"name": role_data["name"]})
            if existing:
                if not skip_existing:
                    existing.description = role_data.get("description", existing.description)
                    existing.permission_names = role_data.get("permission_names", [])
                    await existing.save()
                    imported_roles += 1
                else:
                    skipped_roles += 1
            else:
                role = Role(
                    name=role_data["name"],
                    description=role_data.get("description", ""),
                    permission_names=role_data.get("permission_names", [])
                )
                await role.insert()
                imported_roles += 1
                logger.info(f"Imported role: {role_data['name']}")
    
    # Import users
    if "users" in export_data:
        for user_data in export_data["users"]:
            existing = await User.find_one({"email": user_data["email"]})
            if existing:
                if not skip_existing:
                    # Update existing user
                    existing.username = user_data.get("username", existing.username)
                    existing.full_name = user_data.get("full_name", existing.full_name)
                    existing.hashed_password = user_data.get("hashed_password", existing.hashed_password)
                    existing.is_active = user_data.get("is_active", existing.is_active)
                    existing.is_verified = user_data.get("is_verified", existing.is_verified)
                    existing.company_name = user_data.get("company_name", existing.company_name)
                    existing.position = user_data.get("position", existing.position)
                    existing.role_names = user_data.get("role_names", existing.role_names)
                    await existing.save()
                    imported_users += 1
                    logger.info(f"Updated user: {user_data['email']}")
                else:
                    skipped_users += 1
                    logger.info(f"Skipped existing user: {user_data['email']}")
            else:
                # Create new user
                user = User(
                    email=user_data["email"],
                    username=user_data["username"],
                    full_name=user_data.get("full_name"),
                    hashed_password=user_data["hashed_password"],
                    is_active=user_data.get("is_active", True),
                    is_verified=user_data.get("is_verified", False),
                    company_name=user_data.get("company_name"),
                    position=user_data.get("position"),
                    role_names=user_data.get("role_names", []),
                )
                
                # Set timestamps if provided
                if user_data.get("created_at"):
                    user.created_at = datetime.fromisoformat(user_data["created_at"])
                if user_data.get("updated_at"):
                    user.updated_at = datetime.fromisoformat(user_data["updated_at"])
                if user_data.get("last_login"):
                    user.last_login = datetime.fromisoformat(user_data["last_login"])
                
                await user.insert()
                imported_users += 1
                logger.info(f"Imported user: {user_data['email']}")
    
    return {
        "users": {"imported": imported_users, "skipped": skipped_users},
        "roles": {"imported": imported_roles, "skipped": skipped_roles},
        "permissions": {"imported": imported_permissions, "skipped": skipped_permissions},
    }


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Import users from JSON file to MongoDB")
    parser.add_argument(
        "input_file",
        help="Input JSON file path (exported from export_users.py)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing users/roles/permissions (default: skip existing)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Import Users to MongoDB")
    print("=" * 60)
    print(f"Database: {settings.mongodb_database}")
    print(f"MongoDB URL: {settings.mongodb_url}")
    print(f"Input file: {args.input_file}")
    print(f"Mode: {'Overwrite existing' if args.overwrite else 'Skip existing'}")
    print()
    
    try:
        result = await import_users(args.input_file, skip_existing=not args.overwrite)
        print()
        print("✅ Import completed successfully!")
        print()
        print("Users:")
        print(f"   - Imported: {result['users']['imported']}")
        print(f"   - Skipped: {result['users']['skipped']}")
        print()
        print("Roles:")
        print(f"   - Imported: {result['roles']['imported']}")
        print(f"   - Skipped: {result['roles']['skipped']}")
        print()
        print("Permissions:")
        print(f"   - Imported: {result['permissions']['imported']}")
        print(f"   - Skipped: {result['permissions']['skipped']}")
        return 0
    except Exception as e:
        logger.error("Error importing users", error=str(e))
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
