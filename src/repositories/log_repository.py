from sqlalchemy import select

from src.db.models import LogOrm, VendorOrm
from src.repositories.base_reposiotory import BaseRepository


class LogRepository(BaseRepository):
    async def create(self, app: VendorOrm, time: str, text: str, main_server: bool):
        log = LogOrm(app=app, time=time, text=text, main_server=main_server)

        self.db.add(log)
        await self.db.commit()
        return log
