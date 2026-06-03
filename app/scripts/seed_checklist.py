"""
CHECKLIST SEED SCRIPT

Bu script:
- Checklist bo‘limlarini yaratadi
- Har bir bo‘lim ichiga savollarni qo‘shadi
- Eski checklist ma’lumotlarini tozalaydi

Ishga tushirish:
python -m app.scripts.seed_checklist
"""

import asyncio

from sqlalchemy import delete

from app.core.database import AsyncSessionLocal
from app.modules.checklist.models import ChecklistSection, ChecklistItem
import app.models  # Bu import barcha modellarni yuklaydi, Alembic uchun kerak

async def seed():
    """
    Checklist bo‘limlari va savollarini databasega yozadi.
    """

    async with AsyncSessionLocal() as db:
        # Eski itemlarni birinchi o‘chiramiz,
        # chunki itemlar sectionlarga bog‘langan.
        await db.execute(delete(ChecklistItem))

        # Keyin sectionlarni o‘chiramiz.
        await db.execute(delete(ChecklistSection))

        data = [
            {
                "title": "Внешняя территория",
                "items": [
                    "Парковка чистая",
                    "Входная зона чистая",
                    "Нет мусора вокруг",
                ],
            },
            {
                "title": "Зал",
                "items": [
                    "Пол чистый",
                    "Столы чистые",
                    "Мусорные урны не переполнены",
                ],
            },
             
        ]

        for section_index, section_data in enumerate(data, start=1):
            section = ChecklistSection(
                title_ru=section_data["title"],
                sort_order=section_index,
                is_active=True,
            )

            db.add(section)

            # section.id olish uchun flush qilamiz
            await db.flush()

            for item_index, item_title in enumerate(section_data["items"], start=1):
                item = ChecklistItem(
                    section_id=section.id,
                    title_ru=item_title,
                    requires_photo=False,
                    sort_order=item_index,
                    is_active=True,
                )

                db.add(item)

        await db.commit()

    print("✅ Checklist seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())