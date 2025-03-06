from datetime import datetime

from sqlalchemy import select, and_

from src.db.models.models import LogOrm, TickerOrm, UnsuccessLog
from src.repositories.base_reposiotory import BaseRepository


class TickerRepository(BaseRepository):
    async def all(self) -> list[TickerOrm]:
        tickers = await self.db.execute(select(TickerOrm))
        return tickers.scalars().all()

    async def get(self, slug: str) -> TickerOrm:
        query = select(TickerOrm).where(TickerOrm.slug == slug)
        ticker = await self.db.execute(query)
        return ticker.scalar()

    async def create(self, slug: str, currency: str) -> TickerOrm:
        ticker = TickerOrm(slug=slug, currency=currency)
        self.db.add(ticker)
        await self.db.commit()

        return ticker

    async def create_unsuccesslog(self, body: str) -> None:
        log = UnsuccessLog(body=body)
        self.db.add(log)
        await self.db.commit()
        
    async def exists(self, created_at_l: datetime, created_at_r: datetime) -> bool:
        #exist = await self.db.execute(select(LogOrm))
        exist = await self.db.execute(select(LogOrm).where(and_(LogOrm.created_at<=created_at_r, LogOrm.created_at>=created_at_l)))
        return not (exist.scalars().first() is None)
    
    async def last(self):
        trade = await self.db.execute(select(LogOrm).order_by(LogOrm.id.desc()).limit(1))
        return trade.scalar()