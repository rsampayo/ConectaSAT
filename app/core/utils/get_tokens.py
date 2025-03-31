from app.db.database import get_db
from app.models.user import APIToken

# Get database session
db = next(get_db())

# Get all active tokens
tokens = db.query(APIToken).filter(APIToken.is_active == True).all()

print("Available API tokens:")
if tokens:
    for token in tokens:
        print(f"- Token: {token.token}")
        print(f'  Description: {token.description or "No description"}')
        print(f"  Created at: {token.created_at}")
        print()
else:
    print("No active tokens found.")
