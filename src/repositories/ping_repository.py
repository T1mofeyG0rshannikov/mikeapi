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

    async def exists(self, created_at_l: datetime, created_at_r: datetime) -> bool:
        #exist = await self.db.execute(select(PingOrm))
        exist = await self.db.execute(select(PingOrm).where(and_(PingOrm.created_at<=created_at_r, PingOrm.created_at>=created_at_l)))
        return not (exist.scalars().first() is None)