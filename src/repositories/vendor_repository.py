from sqlalchemy import select

from src.db.mappers.device import from_orm_to_device
from src.db.models.models import APIURLSOrm, DeviceOrm
from src.entites.device import Device
from src.repositories.base_reposiotory import BaseRepository


class DeviceRepository(BaseRepository):
    async def get(self, id: str) -> Device:
        query = select(DeviceOrm).where(DeviceOrm.app_id == id)
        result = await self.db.execute(query)
        device = result.scalar()
        return from_orm_to_device(device) if device else None

    async def get_api_urls(self) -> APIURLSOrm:
        result = await self.db.execute(select(APIURLSOrm))
        return result.scalar()
    
    async def first(self) -> DeviceOrm:
        result = await self.db.execute(select(DeviceOrm).limit(1))
        return result.scalar()
