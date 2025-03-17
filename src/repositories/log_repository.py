from datetime import datetime

from sqlalchemy import select, and_, func

from src.db.models.models import LogOrm, TickerOrm, TraderOrm, UnsuccessLog
from src.repositories.base_reposiotory import BaseRepository
from src.entites.deal import DealOperations


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
        
    async def exists(self, created_at_l: datetime, created_at_r: datetime) -> bool:
        #exist = await self.db.execute(select(LogOrm))
        exist = await self.db.execute(select(LogOrm).where(and_(LogOrm.created_at<=created_at_r, LogOrm.created_at>=created_at_l)))
        return not (exist.scalar() is None)
    
    async def last(self) -> LogOrm:
        trade = await self.db.execute(select(LogOrm).order_by(LogOrm.id.desc()).limit(1))
        return trade.scalar()
    
    async def get_price(self, trader_id: int = None, operation: DealOperations = None):
        filters = and_()
        if trader_id:
            filters &= and_(LogOrm.user_id == trader_id)
        if operation:
            filters &= and_(LogOrm.operation == operation )
        deals = await self.db.execute(select(LogOrm).join(TickerOrm).where(filters))
        deals = deals.scalars().all()
        s = 0
        for deal in deals:
            s += deal.price * deal.ticker.lot
            
        return s
    
    async def filter(self, trader_id: int = None, operation: DealOperations = None, start_time: datetime = None) -> list[LogOrm]:
        filters = and_()
        if trader_id:
            filters &= and_(LogOrm.user_id == trader_id)
        if operation:
            filters &= and_(LogOrm.operation == operation )
        if start_time:
            filters &= and_(LogOrm.created_at >= start_time)
        deals = await self.db.execute(select(LogOrm).join(TickerOrm).where(filters))
        return deals.scalars().all()
