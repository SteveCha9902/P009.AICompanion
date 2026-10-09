import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Default to SQLite if Postgres is unavailable, or read from env
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./companion.db")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        yield session
