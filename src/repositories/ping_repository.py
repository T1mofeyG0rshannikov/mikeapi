from src.db.models.models import PingOrm
from src.repositories.base_reposiotory import BaseRepository
from datetime import datetime
from sqlalchemy import select, and_


class PingRepository(BaseRepository):
    async def create(
        self,
        app_id: int,
    ) -> PingOrm:
        ping = PingOrm(
            app_id=app_id,
        )

        self.db.add(ping)
        await self.db.commit()
        return ping

    async def last(self) -> PingOrm:
        trade = await self.db.execute(select(PingOrm).order_by(PingOrm.id.desc()).limit(1))
        return trade.scalar()