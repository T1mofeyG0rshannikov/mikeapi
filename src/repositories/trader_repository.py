from sqlalchemy import func, select

from src.entites.trader import TraderWatch
from src.db.models.models import TraderOrm, TraderStatisticOrm
from src.repositories.base_reposiotory import BaseRepository


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
    
    async def create_statistics(
        self,
        date,
        trader_id: int,
        cash_balance: float,
        stock_balance: float,
        active_lots: int,
        deals: int,
        trade_volume: float,
        income: float,
        yield_: float,
        gain: float,
        tickers: int
    ) -> None:
        statistics = TraderStatisticOrm(
            date=date,
            trader_id=trader_id,
            cash_balance=cash_balance,
            stock_balance=stock_balance,
            active_lots=active_lots,
            deals=deals,  
            trade_volume=trade_volume,
            income=income,
            yield_=yield_,
            gain=gain,
            tickers=tickers
        )
        self.db.add(statistics)
        await self.db.commit()
