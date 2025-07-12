from datetime import datetime
from sqlalchemy import select, and_, update, func
from sqlalchemy.orm import joinedload

from src.entites.trader import TraderWatch
from src.db.models.models import DealOrm, DeviceOrm, PackageOrm, TickerOrm, TraderOrm
from src.repositories.base_reposiotory import BaseRepository


class SignalRepository(BaseRepository):
    async def filter(
        self, 
        limit: int,
        trader_ids: list[int] = None, 
        ticker_slugs: list[str] = None,
        start_time: datetime = None,
        end_time: datetime = None,
    ) -> list[DealOrm]:
        filters = and_(TickerOrm.is_active==True, TraderOrm.status != TraderWatch.bad)
        if trader_ids:
            filters &= and_(TraderOrm.code.in_(trader_ids))
        if ticker_slugs:
            filters &= and_(TickerOrm.slug.in_(ticker_slugs))
        if start_time:
            filters &= and_(DealOrm.time >= start_time)
        if end_time:
            filters &= and_(DealOrm.time <= end_time)

        deals = await self.db.execute(select(DealOrm).join(TickerOrm).join(TraderOrm).where(filters).options(joinedload(DealOrm.user), joinedload(DealOrm.ticker)).limit(limit))
        return deals.scalars().all()
    
    async def count(
        self,
        trader_ids: list[int] = None, 
        ticker_slugs: list[str] = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> int:
        filters = and_(TickerOrm.is_active==True, TraderOrm.status != TraderWatch.bad)
        if trader_ids:
            filters &= and_(TraderOrm.code.in_(trader_ids))
        if ticker_slugs:
            filters &= and_(TickerOrm.slug.in_(ticker_slugs))
        if start_time:
            filters &= and_(DealOrm.time >= start_time)
        if end_time:
            filters &= and_(DealOrm.time <= end_time)
        
        count = await self.db.execute(select(func.count(DealOrm.id)).join(TickerOrm).join(TraderOrm).where(filters))
        return count.scalar_one()
    
    async def update_many(self, ids: list[int], adopted: bool, adopted_device: DeviceOrm):
        await self.db.execute(update(DealOrm).where(DealOrm.id.in_(ids)).values(adopted=adopted, adopted_device_id=adopted_device.id))
        await self.db.commit()

    async def create_package(
        self,
        signal_ids: list[str],
        device_id: int
    ):
        package = PackageOrm(
            signal_ids=signal_ids,
            device_id=device_id
        )
        self.db.add(package)
        await self.db.commit()
        return package

    async def get_package(self, id: int) -> PackageOrm:
        package = await self.db.execute(select(PackageOrm).where(PackageOrm.id==id).options(joinedload(PackageOrm.device)))
        return package.scalar()