import asyncio
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
import app.models  # Import all models for SQLAlchemy
from app.modules.users.models import User
from app.core.security import hash_password
from app.core.config import settings

async def setup_test_user():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Branch 14 (MW01-UNIVERSAM) da userlarni tekshirish
        result = await session.execute(
            select(User).where(User.branch_id == 14).limit(3)
        )
        users = result.scalars().all()
        
        if users:
            for user in users:
                print(f'Updating - ID: {user.id}, Name: {user.full_name}, Role: {user.role}')
                # Update password
                stmt = update(User).where(User.id == user.id).values(
                    hashed_password=hash_password('12345678'),
                    is_active=True
                )
                await session.execute(stmt)
            await session.commit()
            print('✓ Users updated with password: 12345678')
        else:
            print('No users found in branch 14')
        
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(setup_test_user())
