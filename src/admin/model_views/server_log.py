from sqladmin import ModelView

from src.db.models.models import ServerUnavailableLogOrm


class ServerLogAdmin(ModelView, model=ServerUnavailableLogOrm):
    column_list = [ServerUnavailableLogOrm.id, ServerUnavailableLogOrm.log]

    name = "Ошибки"
    name_plural = "Ошибки"

    column_default_sort = ("id", "desc")

    page_size = 100
