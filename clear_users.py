import asyncio
from sqlalchemy import delete

# SQLAlchemi hamma modellarni tanib olishi uchun ularni import qilamiz
import app.models  # Agar loyihada shu fayl bo'lsa
# Yoki Branch modelini to'g'ridan-to'g'ri import qiling:
# (o'zingizning loyihangizdagi branch modeli yo'lini yozing, masalan:)
# from app.modules.branches.models import Branch 

from app.core.database import AsyncSessionLocal
from app.modules.users.models import User

async def clear_admins():
    async with AsyncSessionLocal() as db:
        print("🗑 Eski adminlarni bazadan o'chirmoqdamiz...")
        
        # Diqqat: SQLAlchemi sinxronizatsiya vaqtida xato bermasligi uchun 
        # execution_options(synchronize_session=False) qo'shamiz
        stmt = (
            delete(User)
            .where(User.username.in_(["sardor", "anton", "asliddin"]))
            .execution_options(synchronize_session=False)
        )
        
        await db.execute(stmt)
        await db.commit()
        print("✅ Eski adminlar o'chirildi. Endi bazangiz toza!")

if __name__ == "__main__":
    asyncio.run(clear_admins())
