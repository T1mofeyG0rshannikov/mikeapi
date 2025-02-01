from src.db.models.models import PingOrm
from src.repositories.base_reposiotory import BaseRepository


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
