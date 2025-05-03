from fastapi import Request
from sqlalchemy import Select
from src.admin.model_views.base import BaseModelView
from src.db.models.models import DeviceOrm
from src.admin.forms import VendorCreateForm


class VendorAdmin(BaseModelView, model=DeviceOrm):
    column_list = [DeviceOrm.app_id, DeviceOrm.auth_token]

    form = VendorCreateForm

    name = "Устройство"
    name_plural = "Устройства"
    
    def form_edit_query(self, request: Request) -> Select:
        return self._stmt_by_identifier(request.path_params["pk"])