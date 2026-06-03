import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, selectinload

# Import all models first
import app.models

from app.modules.users.models import User, UserPasskey
from app.core.config import settings

async def check_admins():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Barcha admin'larni ko'rish
        print("\n📋 Tizimda BARCHA ADMIN'LAR:")
        result = await session.execute(
            select(User).where(User.role == "admin").options(selectinload(User.passkeys))
        )
        all_admins = result.scalars().all()
        
        if all_admins:
            for admin in all_admins:
                print(f"  ✓ {admin.full_name} (ID: {admin.id}, Username: {admin.username}, Active: {admin.is_active})")
                print(f"    └─ Face ID Passkeys: {len(admin.passkeys)} ta")
                for pk in admin.passkeys:
                    print(f"       • {pk.device_name or 'No name'} (ID: {pk.credential_id[:20]}...)")
        else:
            print("  ❌ Hech qanday admin topilmadi!")
        
        # ALLOWED_ADMINS ro'yxatini tekshirish
        print("\n🔍 Face ID UCHUN RUXSAT ETILGAN ADMIN'LAR:")
        ALLOWED_ADMINS = ["Sardor", "Anton", "Asliddin"]
        
        for name in ALLOWED_ADMINS:
            result = await session.execute(
                select(User).where(
                    (User.role == "admin") & 
                    (User.is_active == True) &
                    (User.full_name == name)
                ).options(selectinload(User.passkeys))
            )
            user = result.scalar_one_or_none()
            
            if user:
                print(f"  ✅ {name} TOPILDI!")
                print(f"     • ID: {user.id}")
                print(f"     • Username: {user.username}")
                print(f"     • Active: {user.is_active}")
                print(f"     • Face ID Passkeys: {len(user.passkeys)} ta")
                if not user.passkeys:
                    print("     ⚠️  HECH QANDAY FACE ID REGISTERSIYASI YO'Q!")
            else:
                print(f"  ❌ {name} TOPILMADI!")
        
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(check_admins())
