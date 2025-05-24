# app/db.py

import os
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

# Получаем URL основной БД (например, postgresql+asyncpg://user:pass@localhost/mydb)
DATABASE_URL = os.getenv("DATABASE_URL")

# Разбираем имя БД из URL
from urllib.parse import urlparse
parsed_url = urlparse(DATABASE_URL)
target_db_name = parsed_url.path.lstrip("/")  # Получим mydb

# Системный URL — заменяем имя БД на 'postgres'
admin_db_url = DATABASE_URL.replace(f"/{target_db_name}", "/postgres")

# Engine к системной базе (postgres)
admin_engine = create_async_engine(admin_db_url, echo=False)

async def ensure_database_exists():
    async with admin_engine.connect() as conn:
        # Включаем autocommit, чтобы CREATE DATABASE можно было выполнить
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        
        result = await conn.execute(
            text("SELECT 1 FROM pg_database WHERE datname = :dbname"),
            {"dbname": target_db_name}
        )
        exists = result.scalar()
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{target_db_name}"'))
            print(f"✅ Database '{target_db_name}' created.")
        else:
            print(f"ℹ️  Database '{target_db_name}' already exists.")
    await admin_engine.dispose()

# После создания БД можно инициализировать основной engine
engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()