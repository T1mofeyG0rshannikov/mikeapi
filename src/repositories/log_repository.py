from datetime import datetime

from src.db.models import LogOrm, TraderOrm, VendorOrm
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
