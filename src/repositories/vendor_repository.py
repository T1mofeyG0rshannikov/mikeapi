from sqlalchemy import select

from src.db.models import APIURLSOrm, VendorOrm
from src.repositories.base_reposiotory import BaseRepository


class VendorRepository(BaseRepository):
    async def get(self, id: str) -> VendorOrm:
        query = select(VendorOrm).where(VendorOrm.app_id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_vendor_urls(self) -> APIURLSOrm:
        query = select(APIURLSOrm)
        result = await self.db.execute(query)
        return result.scalars().first()
