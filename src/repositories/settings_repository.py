from sqlalchemy import select

from src.db.models.models import SettingsOrm
from src.repositories.base_reposiotory import BaseRepository


class SettingsRepository(BaseRepository):
    async def get(self) -> SettingsOrm:
        alerts = await self.db.execute(select(SettingsOrm))
        return alerts.scalar()
