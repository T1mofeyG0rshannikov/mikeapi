from src.db.models.models import VendorOrm
from src.entites.vendor import Vendor


def from_orm_to_vendor(vendor: VendorOrm) -> Vendor:
    return Vendor(id=vendor.id, app_id=vendor.app_id, auth_token=vendor.auth_token)
