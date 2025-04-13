from datetime import datetime

from sqlalchemy import select, and_, func, update

from src.db.models.models import DealOrm, LogActivityOrm, TickerOrm, TraderOrm, UnsuccessLog
from src.repositories.base_reposiotory import BaseRepository
from src.entites.deal import DealOperations
from sqlalchemy.orm import joinedload
import pytz


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
        
    async def last(self, ticker_id: int=None, date: datetime = None) -> DealOrm:
        filters = and_()
        if date:
            filters &= and_(func.date(DealOrm.time)==date)
        if ticker_id:
            filters &= and_(DealOrm.ticker_id==ticker_id)

        trade = await self.db.execute(select(DealOrm).join(TickerOrm).where(filters).order_by(DealOrm.time.desc()).limit(1))
        return trade.scalar()
    
    async def filter(
        self, 
        trader_id: int = None, 
        operation: DealOperations = None, 
        start_time: datetime = None,
        ticker_types: list[str] = None,
        ticker_id: int = None
    ) -> list[DealOrm]:
        filters = and_()
        if trader_id:
            filters &= and_(DealOrm.user_id == trader_id)
        if operation:
            filters &= and_(DealOrm.operation == operation )
        if start_time:
            filters &= and_(DealOrm.time >= start_time)
        if ticker_types:
            filters &= and_(TickerOrm.type.in_(ticker_types))
        if ticker_id:
            filters &= and_(DealOrm.ticker_id==ticker_id)
        deals = await self.db.execute(select(DealOrm).join(TickerOrm).where(filters).options(joinedload(DealOrm.ticker)).order_by(DealOrm.time))
        return deals.scalars().all()

    async def update_many(self, update_data: dict, trader_id: int = None, start_time: datetime = None) -> list[DealOrm]:
        filters = and_()
        if trader_id:
            filters &= and_(DealOrm.user_id == trader_id)
        if start_time:
            start_time = datetime(start_time.year, start_time.month, start_time.day)
            timezone = pytz.UTC
            start_time = timezone.localize(start_time)
            filters &= and_(DealOrm.time >= start_time)
        await self.db.execute(update(DealOrm).where(filters).values(**update_data))
        await self.db.commit()

    async def count(self, ticker_id: int = None, time_gte: datetime = None) -> int:
        filters = and_()
        if ticker_id is not None:
            filters &= and_(DealOrm.ticker_id==ticker_id)
        if time_gte is not None:
            filters &= and_(DealOrm.time >= time_gte)

        count = await self.db.execute(select(func.count(DealOrm.id)).where(filters))
        return count.scalar()

    async def all(self):
        result = await self.db.execute(select(DealOrm))
        return result.scalars().all()
    
    async def get_activity(self, date: datetime) -> LogActivityOrm:
        activity = await self.db.execute(select(LogActivityOrm).where(LogActivityOrm.date == date).limit(1))
        return activity.scalar()
    
    async def create_activity(self, date: datetime) -> None:
        activity = LogActivityOrm(date=date)
        self.db.add(activity)
        await self.db.commit()
        return activity
