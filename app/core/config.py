from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):       
    APP_NAME: str = "Shift Checklist API"
    APP_ENV: str = "local"
    DEBUG: bool = True

    DATABASE_URL: str

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
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
        env_file=".env",
        env_file_encoding="utf-8"
    )


settings = Settings()

WORKLY_BASE_URL = settings.WORKLY_BASE_URL
WORKLY_CLIENT_ID = settings.WORKLY_CLIENT_ID
WORKLY_CLIENT_SECRET = settings.WORKLY_CLIENT_SECRET
WORKLY_USERNAME = settings.WORKLY_USERNAME
WORKLY_PASSWORD = settings.WORKLY_PASSWORD
WORKLY_ACCESS_TOKEN = settings.WORKLY_ACCESS_TOKEN
WORKLY_REFRESH_TOKEN = settings.WORKLY_REFRESH_TOKEN