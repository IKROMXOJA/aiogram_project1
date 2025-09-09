from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from collections.abc import AsyncGenerator

from config import ASYNC_DB_URL
from models.base import Base

# ✅ Async engine
engine = create_async_engine(ASYNC_DB_URL, echo=True)

# ✅ Session maker
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ✅ Session generator
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

# ✅ Jadval yaratish (agar kerak bo‘lsa)
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
