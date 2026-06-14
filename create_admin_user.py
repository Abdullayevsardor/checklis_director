# import asyncio
# from app.core.database import AsyncSessionLocal
# from app.core.security import hash_password
# from app.modules.users.models import User
# from sqlalchemy import insert, update, select

# # Barcha modellarni avtomatik ro'yxatdan o'tkazish uchun asosiy ilovani chaqiramiz
# try:
#     import app.main
# except ImportError:
#     pass

# async def create_admin():
#     username = input("Admin username: ").strip()
#     full_name = input("Full name: ").strip()
#     email = input("Phone or email (optional): ").strip() or None
#     password = input("Password: ").strip()
#     confirm = input("Confirm password: ").strip()

#     if password != confirm:
#         print("Error: Passwords do not match.")
#         return

#     hashed = hash_password(password)

#     async with AsyncSessionLocal() as db:
#         # Foydalanuvchi borligini tekshirish
#         stmt = select(User.id).where(User.username == username)
#         result = await db.execute(stmt)
#         existing_id = result.scalar_one_or_none()

#         if existing_id:
#             # Mavjud bo'lsa, obyekt munosabatlariga tegmasdan to'g'ridan-to'g'ri yangilaymiz
#             upd_stmt = (
#                 update(User)
#                 .where(User.id == existing_id)
#                 .values(
#                     full_name=full_name or User.full_name,
#                     phone=email or User.phone,
#                     hashed_password=hashed,
#                     role="admin",
#                     branch_id=None,
#                     is_active=True
#                 )
#             )
#             await db.execute(upd_stmt)
#             await db.commit()
#             print(f"Updated existing admin user: {username}")
#         else:
#             # Yangi bo'lsa, munosabatlarni aylanib o'tib jadval darajasida yozamiz
#             ins_stmt = insert(User.__table__).values(
#                 full_name=full_name,
#                 username=username,
#                 phone=email,
#                 hashed_password=hashed,
#                 role="admin",
#                 branch_id=None,
#                 is_active=True
#             )
#             await db.execute(ins_stmt)
#             await db.commit()
#             print(f"Created admin user: {username}")

#         print("\nAdmin credentials:")
#         print(f"  username: {username}")
#         print(f"  password: {password}")
#         print("  role: admin")

# if __name__ == "__main__":
#     asyncio.run(create_admin())


import sys
import asyncio

# Windows tizimidagi soket (WinError 64) asinxron xatolarini tuzatish
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password
from app.modules.users.models import User
from sqlalchemy import insert, update, select

# Barcha modellarni avtomatik ro'yxatdan o'tkazish uchun asosiy ilovani chaqiramiz
try:
    import app.main
except ImportError:
    pass

async def create_admin():
    username = input("Admin username: ").strip()
    full_name = input("Full name: ").strip()
    email = input("Phone or email (optional): ").strip() or None
    password = input("Password: ").strip()
    confirm = input("Confirm password: ").strip()

    if password != confirm:
        print("Error: Passwords do not match.")
        return

    hashed = hash_password(password)

    async with AsyncSessionLocal() as db:
        # Foydalanuvchi borligini tekshirish
        stmt = select(User.id).where(User.username == username)
        result = await db.execute(stmt)
        existing_id = result.scalar_one_or_none()

        if existing_id:
            # Mavjud bo'lsa, yangilaymiz
            upd_stmt = (
                update(User)
                .where(User.id == existing_id)
                .values(
                    full_name=full_name or User.full_name,
                    phone=email or User.phone,
                    hashed_password=hashed,
                    role="admin",
                    branch_id=None,
                    is_active=True
                )
            )
            await db.execute(upd_stmt)
            await db.commit()
            print(f"Updated existing admin user: {username}")
        else:
            # Yangi bo'lsa, jadval darajasida yozamiz
            ins_stmt = insert(User.__table__).values(
                full_name=full_name,
                username=username,
                phone=email,
                hashed_password=hashed,
                role="admin",
                branch_id=None,
                is_active=True
            )
            await db.execute(ins_stmt)
            await db.commit()
            print(f"Created admin user: {username}")

        print("\nAdmin credentials:")
        print(f"  username: {username}")
        print(f"  password: {password}")
        print("  role: admin")

if __name__ == "__main__":
    asyncio.run(create_admin())
