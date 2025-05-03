from pydantic import BaseModel

from src.schemas.common import DeviceRequest
from src.entites.trader import TraderWatch


class ChangeTradersRequest(DeviceRequest):
    ids: list[str]
    watch: TraderWatch