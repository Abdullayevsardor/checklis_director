import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

# 1. Base model import
try:
    from app.database import Base

    target_metadata = Base.metadata
except ImportError:
    target_metadata = None

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# env.py ichidagi get_url funksiyasini toping va xuddi shu ko'rinishga keltiring:
def get_url():
    # .env yoki alembic.ini dagi hamma narsani chetlab o'tib, docker-compose dagi postgres xizmatiga ulanadi
    user = "checklist"
    password = "password"
    db = "checklist"
    host = "postgres"  # Docker-compose dagi xizmat nomi
    return f"postgresql+asyncpg://{user}:{password}@{host}:5432/{db}"


def run_migrations_offline() -> None:
    """Migrations in 'offline' mode."""
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# Asinxron ulanish qismi (MissingGreenlet xatosini yo'qotadi)
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Migrations in 'online' mode."""
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = get_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
