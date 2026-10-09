import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()
async def main():
    engine = create_async_engine(os.getenv('DATABASE_URL'))
    async with engine.begin() as conn:
        await conn.execute(text("INSERT INTO users (id, created_at, updated_at) VALUES ('test_user_1', NOW(), NOW()) ON CONFLICT (id) DO NOTHING"))

asyncio.run(main())
