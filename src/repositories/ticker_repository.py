from datetime import datetime
from sqlalchemy import select, and_, func, update
from sqlalchemy.orm import selectinload
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

    async def price_exist(self, ticker_id, date) -> bool:
        price = await self.db.execute(select(TickerPriceOrm).where(TickerPriceOrm.date==date, TickerPriceOrm.ticker_id==ticker_id).limit(1))
        price = price.scalar()
        if price:
            return True
        return False
    
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
        price = await self.db.execute(select(TickerPriceOrm).where(TickerPriceOrm.date==date).join(TickerOrm).options(selectinload(TickerPriceOrm.ticker)))
        return price.scalars().all()
    
    async def update_many(self, slugs: list[str], is_active: bool) -> None:
        await self.db.execute(update(TickerOrm).where(TickerOrm.slug.in_(slugs)).values(is_active=is_active))
        await self.db.commit()
