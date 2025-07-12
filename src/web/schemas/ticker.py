from src.web.schemas.common import DeviceRequest


class ChangeTickersRequest(DeviceRequest):
    ids: list[str]
    status: bool
