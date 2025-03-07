import pytz
from fastapi.requests import Request

from sqlalchemy import (
    and_, func, select
)
from starlette.requests import Request
from src.db.database import Session
from src.admin.model_views.base import BaseModelView
from src.db.models.models import LogOrm, SettingsOrm


class LogAdmin(BaseModelView, model=LogOrm):
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

    page_size = 100
    can_export = False

    def filters_from_request(self, request: Request):
        delayed = request.query_params.get("delayed", False)

        if delayed:
            delayed = delayed == "true"
        
        filters = and_()        
        if delayed:
            db = Session()            
            settings = db.execute(select(SettingsOrm)).scalar()

            filters &= and_(
                func.extract('epoch', LogOrm.created_at) - func.extract('epoch', LogOrm.time) >= settings.log_delay
            )

        return filters
