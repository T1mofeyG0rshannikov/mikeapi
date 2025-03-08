from sqlalchemy import func, select

from src.db.models.models import TraderOrm
from src.repositories.base_reposiotory import BaseRepository


class TraderRepository(BaseRepository):
    async def get_codes(self) -> list[str]:
        query = select(TraderOrm.code).order_by(TraderOrm.code)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_many(self, traders: list[TraderOrm]) -> None:
        self.db.add_all(traders)
        await self.db.commit()

    async def get(self, username: str) -> TraderOrm:
        result = await self.db.execute(select(TraderOrm).where(func.lower(TraderOrm.username) == func.lower(username)).limit(1))
        return result.scalar()

    async def create(self, username: str, code: str, watch: str = "new", app_id: int | None = None) -> TraderOrm:
        trader = TraderOrm(username=username, code=code, watch=watch, app_id=app_id)
        self.db.add(trader)
        await self.db.commit()
        return trader

    async def update(self, trader: TraderOrm) -> TraderOrm:
        await self.db.commit()
        await self.db.refresh(trader)
        return trader
    
    async def all(self) -> list[TraderOrm]:
        traders = await self.db.execute(select(TraderOrm))
        return traders.scalars().all()
