from src.db.models.models import PingOrm, ServerUnavailableLogOrm
from src.repositories.base_reposiotory import BaseRepository


class ServerLogRepository(BaseRepository):
    async def create(
        self,
        body: str
    ) -> ServerUnavailableLogOrm:
        log = PingOrm(
            body=body,
        )

        self.db.add(log)
        await self.db.commit()
        return log
