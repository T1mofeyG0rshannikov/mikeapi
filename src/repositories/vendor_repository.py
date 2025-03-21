from sqlalchemy import select

from src.db.mappers.vendor import from_orm_to_device
from src.db.models.models import APIURLSOrm, VendorOrm
from src.entites.vendor import Device
from src.repositories.base_reposiotory import BaseRepository


class VendorRepository(BaseRepository):
    async def get(self, id: str) -> Device:
        query = select(VendorOrm).where(VendorOrm.app_id == id)
        result = await self.db.execute(query)
        device = result.scalar()
        return from_orm_to_device(device) if device else None

    async def get_api_urls(self) -> APIURLSOrm:
        result = await self.db.execute(select(APIURLSOrm))
        return result.scalar()
    
    async def first(self) -> VendorOrm:
        result = await self.db.execute(select(VendorOrm).limit(1))
        return result.scalar()
