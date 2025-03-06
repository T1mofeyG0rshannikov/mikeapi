import pytz
from markupsafe import Markup
from sqladmin import ModelView

from src.db.models.models import UnsuccessLog


class UnsuccesslogAdmin(ModelView, model=UnsuccessLog):
    column_list = [UnsuccessLog.id, UnsuccessLog.created_at, UnsuccessLog.body]

    name = "Неудача"
    name_plural = "Неудачи"

    column_formatters = {
        UnsuccessLog.body: lambda m, a: Markup(f"<pre>{m.body}</pre>" if m.body else ""),
        #UnsuccessLog.created_at: lambda log, _: log.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
        #    "%d.%m.%Y %H:%M:%S"
        #),
    }

    column_default_sort = ("id", "desc")

    page_size = 100
