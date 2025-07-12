from src.web.schemas.common import DeviceRequest
from src.entites.trader import TraderWatch


class ChangeTradersRequest(DeviceRequest):
    ids: list[str]
    watch: TraderWatch