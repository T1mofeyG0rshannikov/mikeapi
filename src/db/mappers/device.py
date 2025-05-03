from src.db.models.models import DeviceOrm
from src.entites.device import Device


def from_orm_to_device(device: DeviceOrm) -> Device:
    return Device(id=device.id, app_id=device.app_id, auth_token=device.auth_token)
