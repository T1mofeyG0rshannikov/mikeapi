from datetime import datetime

from sqlalchemy import select

from src.db.models import LogOrm, TickerOrm, TraderOrm, VendorOrm
from src.repositories.base_reposiotory import BaseRepository


class LogRepository(BaseRepository):
    async def create(
        self,
        app: VendorOrm,
        time: datetime,
        main_server: bool,
        user: TraderOrm,
        currency: str,
        price: float,
        ticker: str,
        operation: str,
    ) -> LogOrm:
        log = LogOrm(
            app=app,
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
