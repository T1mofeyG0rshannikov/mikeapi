from src.admin.model_views.base import BaseModelView
from src.db.models.models import SettingsOrm


class SettingsAdmin(BaseModelView, model=SettingsOrm):
    column_list = [SettingsOrm.commission, SettingsOrm.start_date]

    name = "Настройки"
    name_plural = "Настройки"
