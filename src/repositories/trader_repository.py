from sqlalchemy import func, select, delete, and_

from src.entites.trader import StatisticPeriodEnum, TraderWatch
from src.db.models.models import TraderOrm, TraderStatisticOrm
from src.repositories.base_reposiotory import BaseRepository
from datetime import datetime


class TraderRepository(BaseRepository):
    async def get_codes(self) -> list[str]:
        result = await self.db.execute(select(TraderOrm.code).order_by(TraderOrm.code))
        return result.scalars().all()

    async def create_many(self, traders: list[TraderOrm]) -> None:
        self.db.add_all(traders)
        await self.db.commit()

    async def get(self, username: str) -> TraderOrm:
        result = await self.db.execute(select(TraderOrm).where(func.lower(TraderOrm.username) == func.lower(username)).limit(1))
        return result.scalar()

    async def create(self, username: str, code: str, watch: TraderWatch = "new", app_id: int | None = None) -> TraderOrm:
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

    async def filter(self, watch: TraderWatch) -> list[TraderOrm]:
        traders = await self.db.execute(select(TraderOrm).where(TraderOrm.watch==watch))
        return traders.scalars().all()
    
    async def last_statistics(self, trader_id: int, period: str) -> TraderStatisticOrm:
        last = await self.db.execute(select(TraderStatisticOrm).where(TraderStatisticOrm.trader_id==trader_id, TraderStatisticOrm.period==period).order_by(TraderStatisticOrm.id.desc()).limit(1))
        return last.scalar()
    
    async def create_statistics(
        self,
        date: datetime,
        end_date: datetime,
        start_date: datetime,
        period: StatisticPeriodEnum,
        date_value: str,
        trader_id: int,
        cash_balance: float,
        stock_balance: float,
        active_lots: int,
        deals: int,
        trade_volume: float,
        income: float,
        yield_: float,
        gain: float,
        tickers: int,
        deals_degrees: int = None,
        active_lots_degrees: int = None,
        stock_balance_degrees: float = None,
        cash_balance_degrees: float = None,
        trade_volume_degrees: float = None,
        income_degrees: float = None,
        yield_degrees: float = None,
        gain_degrees: float = None,
        tickers_degrees: int = None
    ) -> TraderStatisticOrm:
        statistics = TraderStatisticOrm(
            date=date,
            start_date=start_date,
            end_date=end_date,
            date_value=date_value,
            period=period,
            trader_id=trader_id,
            cash_balance=cash_balance,
            cash_balance_degrees=cash_balance_degrees,
            stock_balance=stock_balance,
            stock_balance_degrees=stock_balance_degrees,
            active_lots=active_lots,
            active_lots_degrees=active_lots_degrees,
            deals=deals,  
            deals_degrees=deals_degrees,  
            trade_volume=trade_volume,
            trade_volume_degrees=trade_volume_degrees,
            income=income,
            income_degrees=income_degrees,
            yield_=yield_,
            yield_degrees=yield_degrees,
            gain=gain,
            gain_degrees=gain_degrees,
            tickers=tickers,
            tickers_degrees=tickers_degrees
        )
        self.db.add(statistics)
        await self.db.commit()
        return statistics
        
    async def filter_by_usernames(self, usernames: list[str]) -> list[TraderOrm]:
        traders = []
        for i in range(0, len(usernames), 5000):
            result = await self.db.execute(select(TraderOrm).where(TraderOrm.username.in_(usernames[i : i + 5000])))
            traders.extend(result.scalars().all())
        
        return traders
    
    async def get_usernames(self) ->list[str]:
        usernames = await self.db.execute(select(TraderOrm.username))
        return usernames.scalars().all()
        
    async def delete_statistics(self, period: StatisticPeriodEnum = None, date: datetime = None) -> None:
        filters = and_()
        if period:
            filters &= and_(TraderStatisticOrm.period==period)
        if date:
            filters &= and_(TraderStatisticOrm.date==date)

        await self.db.execute(delete(TraderStatisticOrm).where(filters))
