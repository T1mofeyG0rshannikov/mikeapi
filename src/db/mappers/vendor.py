from src.db.models.models import VendorOrm
from src.entites.vendor import Device


def from_orm_to_device(device: VendorOrm) -> Device:
    return Device(id=device.id, app_id=device.app_id, auth_token=device.auth_token)
