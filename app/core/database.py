from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import os

# Agar lokalda bo'lsa, SSL ni butunlay o'chiramiz
connect_args = {}
if "RAILWAY_ENVIRONMENT" not in os.environ:
    connect_args = {
        "ssl": False  # Lokal bazaga oddiy (SSL siz) ulanishni majburlaydi
    }

 
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    connect_args=connect_args # Shuni qo'shing

)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session