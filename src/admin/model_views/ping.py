import pytz
from src.admin.model_views.base import BaseModelView
from src.db.models.models import PingOrm


class PingAdmin(BaseModelView, model=PingOrm):
    column_list = [PingOrm.id, PingOrm.app, PingOrm.created_at]

    name = "Пинг"
    name_plural = "Пинг"

    column_formatters = {
        PingOrm.created_at: lambda ping, _: ping.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y %H:%M:%S"
        )
    }

    column_default_sort = ("id", "desc")

    page_size = 100
