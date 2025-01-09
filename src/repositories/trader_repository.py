from sqlalchemy import select

from src.db.models import TraderOrm
from src.repositories.base_reposiotory import BaseRepository


class TraderRepository(BaseRepository):
    async def get_codes(self):
        query = select(TraderOrm.code)
        result = await self.db.execute(query)
        return result.scalars().all()
