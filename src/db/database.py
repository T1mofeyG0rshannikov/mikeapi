from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.db.db_config import get_db_config

SQLALCHEMY_DATABASE_URL = get_db_config().DATABASE_URL

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

new_session = async_sessionmaker(engine, expire_on_commit=False)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


class Model(DeclarativeBase):
    pass


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)


async def get_db():
    async with new_session() as session:
        yield session
