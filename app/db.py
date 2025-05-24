# app/db.py
import os
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from dotenv import load_dotenv
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import Base, User
from urllib.parse import urlparse

load_dotenv()

raw_url = os.getenv("DATABASE_URL")
if os.getenv("DOCKER") == "1":
    parsed = urlparse(raw_url)
    new_netloc = parsed.netloc.replace("localhost", "db")
    DATABASE_URL = raw_url.replace(parsed.netloc, new_netloc)
else:
    DATABASE_URL = raw_url

from urllib.parse import urlparse
parsed_url = urlparse(DATABASE_URL)
target_db_name = parsed_url.path.lstrip("/")  

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
            print(f"Database '{target_db_name}' created.")
        else:
            print(f"Database '{target_db_name}' already exists.")
    await admin_engine.dispose()

# После создания БД можно инициализировать основной engine
engine = create_async_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

async def save_users(users):
    async with SessionLocal() as session:
        session.add_all(users)
        await session.commit()
        
async def get_user_from_db(user_id: int):
    async with SessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
async def get_users(page: int = 1, limit: int = 20):
    offset = (page - 1) * limit
    async with SessionLocal() as session:
        result = await session.execute(select(User).offset(offset).limit(limit))
        users = result.scalars().all()
        total_users = await session.scalar(select(func.count()).select_from(User))
        total_pages = (total_users + limit - 1) // limit  # округление вверх
        return users, page, total_pages
    