from datetime import datetime, timedelta

from sqlalchemy import select, exists, and_

from src.db.models.models import LogOrm, TickerOrm, TraderOrm, UnsuccessLog
from src.repositories.base_reposiotory import BaseRepository


class LogRepository(BaseRepository):
    async def create(
        self,
        app_id: int,
        time: datetime,
        main_server: bool,
        user: TraderOrm,
        currency: str,
        price: float,
        ticker: str,
        operation: str,
    ) -> LogOrm:
        log = LogOrm(
            app_id=app_id,
            time=time,
            main_server=main_server,
            user=user,
            currency=currency,
            price=price,
            ticker=ticker,
            operation=operation,
        )

        self.db.add(log)
        await self.db.commit()
        return log

    async def get_ticker(self, slug: str) -> TickerOrm:
        query = select(TickerOrm).where(TickerOrm.slug == slug)
        ticker = await self.db.execute(query)
        return ticker.scalars().first()

    async def create_ticker(self, slug: str, currency: str) -> TickerOrm:
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