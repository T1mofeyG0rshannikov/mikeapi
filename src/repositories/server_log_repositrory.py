from src.db.models.models import ServerUnavailableLogOrm
from src.repositories.base_reposiotory import BaseRepository


class ServerLogRepository(BaseRepository):
    async def create(
        self,
        body: str
    ) -> ServerUnavailableLogOrm:
        log = ServerUnavailableLogOrm(
            log=body,
        )

        self.db.add(log)
        await self.db.commit()
        return log
