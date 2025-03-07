from fastapi import Request
from sqlalchemy import Select
from src.admin.model_views.base import BaseModelView
from src.db.models.models import VendorOrm
from src.admin.forms import VendorCreateForm


class VendorAdmin(BaseModelView, model=VendorOrm):
    column_list = [VendorOrm.app_id, VendorOrm.auth_token]

    form = VendorCreateForm

    name = "Приложение"
    name_plural = "Приложения"
    
    def form_edit_query(self, request: Request) -> Select:
        return self._stmt_by_identifier(request.path_params["pk"])