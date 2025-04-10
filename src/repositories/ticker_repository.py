from datetime import datetime
from sqlalchemy import select, and_, func

from src.db.models.models import DealOrm, TickerOrm, TickerPriceOrm
from src.repositories.base_reposiotory import BaseRepository


class TickerRepository(BaseRepository):
    async def all(self) -> list[TickerOrm]:
        tickers = await self.db.execute(select(TickerOrm))
        return tickers.scalars().all()

    async def get(self, slug: str) -> TickerOrm:
        ticker = await self.db.execute(select(TickerOrm).where(TickerOrm.slug == slug))
        return ticker.scalar()

    async def create(self, slug: str, currency: str) -> TickerOrm:
        ticker = TickerOrm(slug=slug, currency=currency)
        self.db.add(ticker)
        await self.db.commit()

        return ticker
 
    async def count(self, trader_id: int) -> int:
        query = select(func.count(TickerOrm.id))
        filters = and_()
        if trader_id:
            query = query.join(DealOrm)
            filters &= and_(DealOrm.user_id==trader_id)

        result = await self.db.execute(query.where(filters))
        return result.scalar_one()
    
    async def update(self, ticker: TickerOrm) -> None:
        await self.db.refresh(ticker)
        await self.db.commit()

    async def create_ticker_price(self, ticker_id: int, price: int, date: datetime) -> TickerPriceOrm:
        ticker_price = TickerPriceOrm(
            price=price,
            date=date,
            ticker_id=ticker_id
        )
        self.db.add(ticker_price)
        await self.db.commit()
        return ticker_price
    
    async def get_ticker_price(self, date: datetime) -> float:
        price = await self.db.execute(select(TickerPriceOrm).where(TickerPriceOrm.date==date).join(TickerOrm))
        return price.scalars().all()