from datetime import datetime

from sqlalchemy import select, and_

from src.db.models.models import LogOrm, TickerOrm, TraderOrm, UnsuccessLog
from src.repositories.base_reposiotory import BaseRepository
from src.entites.deal import DealOperations
from sqlalchemy.orm import joinedload


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

    async def create_unsuccesslog(self, body: str) -> None:
        log = UnsuccessLog(body=body)
        self.db.add(log)
        await self.db.commit()
        
    async def last(self, ticker_slug: str=None) -> LogOrm:
        filters = and_()
        if ticker_slug:
            filters &= and_(TickerOrm.slug==ticker_slug)

        trade = await self.db.execute(select(LogOrm).where(filters).order_by(LogOrm.id.desc()).limit(1))
        return trade.scalar()
    
    async def filter(self, trader_id: int = None, operation: DealOperations = None, start_time: datetime = None) -> list[LogOrm]:
        filters = and_()
        if trader_id:
            filters &= and_(LogOrm.user_id == trader_id)
        if operation:
            filters &= and_(LogOrm.operation == operation )
        if start_time:
            filters &= and_(LogOrm.created_at >= start_time)
        deals = await self.db.execute(select(LogOrm).join(TickerOrm).where(filters).options(joinedload(LogOrm.ticker)))
        return deals.scalars().all()
