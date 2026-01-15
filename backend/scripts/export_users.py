"""Script to export users from MongoDB to JSON file"""
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


async def export_users(output_file: str = "users_export.json"):
    """Export all users, roles, and permissions to JSON file"""
    # Connect to MongoDB
    await connect_to_mongo()
    await init_beanie()
    
    # Export data
    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "database": settings.mongodb_database,
        "users": [],
        "roles": [],
        "permissions": []
    }
    
    # Export users
    users = await User.find_all().to_list()
    logger.info(f"Found {len(users)} users to export")
    
    for user in users:
        user_data = {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "hashed_password": user.hashed_password,  # Export password hash
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "company_name": user.company_name,
            "position": user.position,
            "role_names": user.role_names,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
            "last_login": user.last_login.isoformat() if user.last_login else None,
        }
        export_data["users"].append(user_data)
    
    # Export roles
    roles = await Role.find_all().to_list()
    logger.info(f"Found {len(roles)} roles to export")
    
    for role in roles:
        role_data = {
            "name": role.name,
            "description": role.description,
            "permission_names": role.permission_names,
        }
        export_data["roles"].append(role_data)
    
    # Export permissions
    permissions = await Permission.find_all().to_list()
    logger.info(f"Found {len(permissions)} permissions to export")
    
    for permission in permissions:
        permission_data = {
            "name": permission.name,
            "description": permission.description,
        }
        export_data["permissions"].append(permission_data)
    
    # Save to file
    output_path = Path(output_file)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"Exported {len(export_data['users'])} users, {len(export_data['roles'])} roles, {len(export_data['permissions'])} permissions to {output_path}")
    
    return export_data


async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Export users from MongoDB")
    parser.add_argument(
        "-o", "--output",
        default="users_export.json",
        help="Output JSON file path (default: users_export.json)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Export Users from MongoDB")
    print("=" * 60)
    print(f"Database: {settings.mongodb_database}")
    print(f"MongoDB URL: {settings.mongodb_url}")
    print(f"Output file: {args.output}")
    print()
    
    try:
        export_data = await export_users(args.output)
        print()
        print("✅ Export completed successfully!")
        print(f"   - Users: {len(export_data['users'])}")
        print(f"   - Roles: {len(export_data['roles'])}")
        print(f"   - Permissions: {len(export_data['permissions'])}")
        print(f"   - File: {args.output}")
        return 0
    except Exception as e:
        logger.error("Error exporting users", error=str(e))
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
