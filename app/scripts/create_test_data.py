"""
TEST DATA SCRIPT

Bu script:
- eski test ma'lumotlarni tozalaydi
- test branch yaratadi
- test director yaratadi

Login uchun:
username: max
password: 1431
"""

import asyncio

import app.models  # relationship'larni yuklash uchun MUHIM

from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.core.security import hash_password

from app.modules.branches.models import Branch
from app.modules.users.models import User

from app.modules.shift_checks.models import (
    ShiftCheck,
    CheckAnswer,
    AnswerPhoto,
)


async def seed():

    async with AsyncSessionLocal() as db:

        print("🧹 Cleaning old test data...")

        # Shift check related data
        await db.execute(delete(AnswerPhoto))
        await db.execute(delete(CheckAnswer))
        await db.execute(delete(ShiftCheck))

        # Faqat test userni o‘chiramiz
        await db.execute(
            delete(User).where(User.username == "max")
        )

        # Faqat test branchni o‘chiramiz
        await db.execute(
            delete(Branch).where(Branch.name == "Test filial")
        )

        await db.commit()

        print("✅ Old test data removed")

        # 🔥 Branch yaratamiz
        branch = Branch(
            name="Test filial",
            address="Tashkent",
            is_active=True,
        )

        db.add(branch)

        # branch.id olish uchun
        await db.flush()

        print(f"✅ Branch created: {branch.name}")

        # 🔥 Director user yaratamiz
        user = User(
            workly_employee_id="test-director",
            full_name="Test Director",
            username="max",
            hashed_password=hash_password("1431"),
            role="director",
            branch_id=branch.id,
            is_active=True,
        )

        db.add(user)

        await db.commit()

        print("✅ Test director created!")
        print(f"User ID: {user.id}")
        print(f"Branch ID: {branch.id}")

        print("\nLOGIN DATA:")
        print("username: max")
        print("password: 1431")


if __name__ == "__main__":
    asyncio.run(seed())