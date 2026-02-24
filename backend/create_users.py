from database.db import SessionLocal
from auth.models import User
from auth.auth_utils import hash_password

db = SessionLocal()

users = [
    ("demo", "demo@example.com", "demo123", True),
    ("vanthu suresh", "vanthu@example.com", "vanthu 1234", False),
    ("varthu", "varthu@example.com", "varthu1234", False),
]

for username, email, password, is_premium in users:
    existing = db.query(User).filter(User.username == username).first()
    if not existing:
        user = User(username=username, email=email, password_hash=hash_password(password), is_premium=is_premium)
        db.add(user)
        print(f"✓ Created {username}")
    else:
        print(f"✓ {username} already exists")

db.commit()
db.close()
