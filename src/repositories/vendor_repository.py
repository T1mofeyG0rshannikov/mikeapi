from sqlalchemy import select

from src.db.mappers.vendor import from_orm_to_vendor
from src.db.models.models import APIURLSOrm, VendorOrm
from src.entites.vendor import Vendor
from src.repositories.base_reposiotory import BaseRepository


class VendorRepository(BaseRepository):
    async def get(self, id: str) -> Vendor:
        query = select(VendorOrm).where(VendorOrm.app_id == id)
        result = await self.db.execute(query)
        vendor_db = result.scalars().first()
        return from_orm_to_vendor(vendor_db) if vendor_db else None

    async def get_vendor_urls(self) -> APIURLSOrm:
        query = select(APIURLSOrm)
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def first(self) -> VendorOrm:
        query = select(VendorOrm)
        result = await self.db.execute(query)
        return result.scalars().first()
