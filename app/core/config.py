# from pydantic_settings import BaseSettings, SettingsConfigDict


# class Settings(BaseSettings):       
#     APP_NAME: str = "Shift Checklist API"
#     APP_ENV: str = "local"
#     DEBUG: bool = True

#     DATABASE_URL: str

#     SECRET_KEY: str
#     ALGORITHM: str = "HS256"
#     ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

#     WORKLY_BASE_URL: str
#     WORKLY_CLIENT_ID: str
#     WORKLY_CLIENT_SECRET: str
#     WORKLY_USERNAME: str | None = None
#     WORKLY_PASSWORD: str | None = None
#     WORKLY_ACCESS_TOKEN: str | None = None
#     WORKLY_REFRESH_TOKEN: str | None = None

#     S3_ENDPOINT_URL: str
#     S3_ACCESS_KEY: str
#     S3_SECRET_KEY: str
#     S3_BUCKET: str
#     S3_REGION: str = "us-east-1"

#     REDIS_URL: str

#     model_config = SettingsConfigDict(
#         env_file=".env",
#         env_file_encoding="utf-8"
#     )


# settings = Settings()

# WORKLY_BASE_URL = settings.WORKLY_BASE_URL
# WORKLY_CLIENT_ID = settings.WORKLY_CLIENT_ID
# WORKLY_CLIENT_SECRET = settings.WORKLY_CLIENT_SECRET
# WORKLY_USERNAME = settings.WORKLY_USERNAME
# WORKLY_PASSWORD = settings.WORKLY_PASSWORD
# WORKLY_ACCESS_TOKEN = settings.WORKLY_ACCESS_TOKEN
# WORKLY_REFRESH_TOKEN = settings.WORKLY_REFRESH_TOKEN




import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Kod qayerda ishlayotganini aniqlaymiz
IS_RAILWAY = "RAILWAY_ENVIRONMENT" in os.environ

# 2. Agar lokalda bo'lsa ishlatiladigan standart baza manzili
LOCAL_DB = "postgresql+asyncpg://checklist:password@localhost:5432/checklist"


class Settings(BaseSettings):       
    APP_NAME: str = "Shift Checklist API"
    APP_ENV: str = "production" if IS_RAILWAY else "local"
    DEBUG: bool = not IS_RAILWAY # Serverda False, lokalda True bo'ladi

    # 3. Agar Railway o'zining DATABASE_URL o'zgaruvchisini bersa o'shani oladi,
    # berilmagan taqdirda (lokalda) LOCAL_DB ni standart qiymat sifatida ishlatadi.
    DATABASE_URL: str = os.environ.get("DATABASE_URL", LOCAL_DB)

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normalize_database_url(cls, value):
        if isinstance(value, str):
            if value.startswith("postgres://"):
                return value.replace("postgres://", "postgresql+asyncpg://", 1)
            if value.startswith("postgresql://") and not value.startswith("postgresql+asyncpg://"):
                return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    WORKLY_BASE_URL: str
    WORKLY_CLIENT_ID: str
    WORKLY_CLIENT_SECRET: str
    WORKLY_USERNAME: str | None = None
    WORKLY_PASSWORD: str | None = None
    WORKLY_ACCESS_TOKEN: str | None = None
    WORKLY_REFRESH_TOKEN: str | None = None

    S3_ENDPOINT_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_BUCKET: str
    S3_REGION: str = "us-east-1"

    REDIS_URL: str

    model_config = SettingsConfigDict(
        # Agar lokalda .env fayli topilmasa, xato bermasligi uchun extra qo'shildi
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" 
    )


settings = Settings()

WORKLY_BASE_URL = settings.WORKLY_BASE_URL
WORKLY_CLIENT_ID = settings.WORKLY_CLIENT_ID
WORKLY_CLIENT_SECRET = settings.WORKLY_CLIENT_SECRET
WORKLY_USERNAME = settings.WORKLY_USERNAME
WORKLY_PASSWORD = settings.WORKLY_PASSWORD
WORKLY_ACCESS_TOKEN = settings.WORKLY_ACCESS_TOKEN
WORKLY_REFRESH_TOKEN = settings.WORKLY_REFRESH_TOKEN

# Convenience accessor for libraries that expect a plain PostgreSQL DSN
# (e.g. asyncpg.connect) which does not accept the SQLAlchemy-style
# scheme 'postgresql+asyncpg://'. Use `ASYNCPG_DATABASE_URL` when calling
# asyncpg directly; use `settings.DATABASE_URL` for SQLAlchemy engines.
def _asyncpg_dsn_from(url: str) -> str:
    if isinstance(url, str) and url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://", 1)
    return url

ASYNCPG_DATABASE_URL = _asyncpg_dsn_from(settings.DATABASE_URL)
