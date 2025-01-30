import pytz
from fastapi.requests import Request
from sqladmin import ModelView, action
from sqladmin.helpers import slugify_class_name
from sqlalchemy import delete
from starlette.responses import RedirectResponse

from src.db.models import (
    LogOrm,
)


class LogAdmin(ModelView, model=LogOrm):
    column_list = [
        LogOrm.app,
        LogOrm.time,
        LogOrm.user,
        LogOrm.operation,
        LogOrm.ticker,
        LogOrm.price,
        LogOrm.currency,
        LogOrm.created_at,
        LogOrm.main_server,
    ]

    name = "Сделка"
    name_plural = "Сделки"
    list_template = "sqladmin/list-logs.html"

    column_default_sort = ("created_at", True)
    column_formatters = {
        LogOrm.app: lambda log, _: str(log.app),
        LogOrm.created_at: lambda log, _: log.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y %H:%M:%S"
        ),
        LogOrm.time: lambda log, _: log.time.astimezone(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y %H:%M:%S"),
    }

    column_labels = {
        "app": "Устройство",
        "time": "Время",
        "user": "Трейдер",
        "operation": "Сделка",
        "currency": "Валюта",
        "ticker": "Тикер",
        "price": "Цена",
        "created_at": "Создан",
        "main_server": "Сервер",
    }

    @action(name="delete_all", label="Удалить все", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            await session.execute(delete(self.model))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    page_size = 100
    can_export = False
