import pytz
from fastapi.requests import Request

from starlette.requests import Request
from src.db.database import Session
from src.admin.model_views.base import BaseModelView
from src.db.models.models import LogOrm, SettingsOrm
from sqladmin.pagination import Pagination
from sqlalchemy.orm import selectinload

from sqlalchemy import (
    and_,
    select,
    func
)
from datetime import datetime


class DealAdmin(BaseModelView, model=LogOrm):
    column_list = [
        LogOrm.app,
        LogOrm.time,
        LogOrm.user,
        LogOrm.operation,
        LogOrm.ticker,
        LogOrm.price,
        LogOrm.currency,
        LogOrm.created_at,
        LogOrm.time,
        LogOrm.main_server,
    ]
    
    column_sortable_list = [
        LogOrm.created_at,
        LogOrm.time,
    ]

    name = "Сделка"
    name_plural = "Сделки"
    list_template = "sqladmin/list-logs.html"

    column_default_sort = ("id", "desc")
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
        trader_id = request.query_params.get("trader_id")
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")
        
        if delayed:
            delayed = delayed == "true"
        
        filters = and_()        
        if delayed:
            db = Session()            
            settings = db.execute(select(SettingsOrm)).scalar()

            filters &= and_(
                func.extract('epoch', LogOrm.created_at) - func.extract('epoch', LogOrm.time) >= settings.log_delay
            )

        if trader_id:
            filters &= and_(LogOrm.user_id==int(trader_id))
        if start_date:
            filters &= and_(LogOrm.created_at >= datetime.strptime(start_date, "%d.%m.%Y"))
        if end_date:
            filters &= and_(LogOrm.created_at <= datetime.strptime(end_date, "%d.%m.%Y"))

        return filters
    
    
    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))

        stmt = self.list_query(request).filter(self.filters_from_request(request))
        for relation in self._list_relations:
            stmt = stmt.options(selectinload(relation))

        stmt = self.sort_query(stmt, request)

        count = await self.count(request, select(func.count()).select_from(stmt))

        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        rows = await self._run_query(stmt)
        
        db = Session()            
        settings = db.execute(select(SettingsOrm)).scalar()

        for row in rows:
            row.delayed = (row.created_at - row.time).total_seconds() >= settings.log_delay
        
        pagination = Pagination(
            rows=rows,
            page=page,
            page_size=page_size,
            count=count,
        )

        return pagination
