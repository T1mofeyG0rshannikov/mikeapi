from datetime import datetime

from sqlalchemy import select, and_, func

from src.db.models.models import DealOrm, TickerOrm, TraderOrm, UnsuccessLog
from src.repositories.base_reposiotory import BaseRepository
from src.entites.deal import DealOperations
from sqlalchemy.orm import joinedload


class DealRepository(BaseRepository):
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
    ) -> DealOrm:
        log = DealOrm(
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
        
    async def last(self, ticker_slug: str=None) -> DealOrm:
        filters = and_()
        if ticker_slug:
            filters &= and_(TickerOrm.slug==ticker_slug)

        trade = await self.db.execute(select(DealOrm).where(filters).order_by(DealOrm.id.desc()).limit(1))
        return trade.scalar()
    
    async def filter(self, trader_id: int = None, operation: DealOperations = None, start_time: datetime = None) -> list[DealOrm]:
        filters = and_()
        if trader_id:
            filters &= and_(DealOrm.user_id == trader_id)
        if operation:
            filters &= and_(DealOrm.operation == operation )
        if start_time:
            filters &= and_(DealOrm.created_at >= start_time)
        deals = await self.db.execute(select(DealOrm).join(TickerOrm).where(filters).options(joinedload(DealOrm.ticker)))
        return deals.scalars().all()

    async def count(self, ticker_id: int = None, time_gte: datetime = None) -> int:
        filters = and_()
        if ticker_id is not None:
            filters &= and_(DealOrm.ticker_id==ticker_id)
        if time_gte is not None:
            filters &= and_(DealOrm.time >= time_gte)

        count = await self.db.execute(select(func.count(DealOrm.id)).where(filters))
        return count.scalar()