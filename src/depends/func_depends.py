from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import SessionLocal
from src.repositories.user_repository import UserRepository


def get_user_repository(db: AsyncSession = SessionLocal()) -> UserRepository:
    return UserRepository(db)
