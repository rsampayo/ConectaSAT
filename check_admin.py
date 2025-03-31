from app.db.database import get_db
from app.models.user import SuperAdmin

# Get the database session
db = next(get_db())

# Query all admin users
admins = db.query(SuperAdmin).all()

print(f"Found {len(admins)} admin users:")
for admin in admins:
    print(f"- {admin.username} (Active: {admin.is_active})") 