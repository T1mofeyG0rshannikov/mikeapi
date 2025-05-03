from src.schemas.common import DeviceRequest


class ChangeTickersRequest(DeviceRequest):
    ids: list[str]
    status: bool
