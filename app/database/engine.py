from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.database.models import Base
from config import settings

engine = create_async_engine(settings.db_url)
session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

