from sqladmin import ModelView

from src.db.models.models import SettingsOrm


class SettingsAdmin(ModelView, model=SettingsOrm):
    column_list = [SettingsOrm.commission, SettingsOrm.start_date]

    name = "Настройки"
    name_plural = "Настройки"
