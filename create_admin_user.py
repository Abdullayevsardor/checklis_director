import asyncio

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.modules.users.models import User


def print_help():
    print("Usage: python create_admin_user.py")
    print("Then follow the prompts to create or update the admin account.")


async def create_admin():
    username = input("Admin username: ").strip()
    full_name = input("Full name: ").strip()
    email = input("Phone or email (optional): ").strip() or None
    password = input("Password: ").strip()
    confirm = input("Confirm password: ").strip()

    if password != confirm:
        print("Error: Passwords do not match.")
        return

    async with AsyncSessionLocal() as db:
        stmt = await db.execute(
            User.__table__.select().where(User.username == username)
        )
        existing = stmt.first()

        if existing:
            user_id = existing[0]
            user = await db.get(User, user_id)
            user.full_name = full_name or user.full_name
            user.phone = email or user.phone
            user.hashed_password = hash_password(password)
            user.role = "admin"
            user.branch_id = None
            user.is_active = True
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"Updated existing admin user: {user.username} (id={user.id})")
        else:
            user = User(
                full_name=full_name,
                username=username,
                phone=email,
                hashed_password=hash_password(password),
                role="admin",
                branch_id=None,
                is_active=True,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            print(f"Created admin user: {user.username} (id={user.id})")

        print("\nAdmin credentials:")
        print(f"  username: {user.username}")
        print(f"  password: {password}")
        print("  role: admin")
        print("  branch_id: None")


if __name__ == "__main__":
    asyncio.run(create_admin())
