from typing import List
import pytz
from fastapi.requests import Request

from starlette.requests import Request
from src.db.database import Session
from src.admin.model_views.base import BaseModelView
from src.db.models.models import DealOrm, SettingsOrm
from sqladmin.pagination import Pagination
from sqlalchemy.orm import selectinload


from sqlalchemy import (
    and_,
    select,
    func
)
from datetime import datetime, timedelta
from markupsafe import Markup


operation_colors = {
    "buy": "(20, 215, 20)",
    "sell": "(255, 100, 100)",
}

class DealAdmin(BaseModelView, model=DealOrm):
    column_list = [
        DealOrm.app,
        DealOrm.user,
        DealOrm.operation,
        DealOrm.ticker,
        DealOrm.price,
        DealOrm.currency,
        DealOrm.created_at,
        DealOrm.time,
        DealOrm.main_server,
    ]

    trader_column_list = [
        DealOrm.user,
        DealOrm.operation,
        DealOrm.ticker,
        DealOrm.price,
        DealOrm.currency,
        DealOrm.created_at,
        DealOrm.time,
    ]
    
    def get_dynamic_list_columns(self, request: Request) -> List[str]:
        """Get list of properties to display in List page."""

        if request.query_params.get("trader_id", None):
            column_list = getattr(self, "trader_column_list", None)
        else:
            column_list = getattr(self, "column_list", None)

        column_exclude_list = getattr(self, "column_exclude_list", None)

        return self._build_column_list(
            include=column_list,
            exclude=column_exclude_list,
            defaults=[pk.name for pk in self.pk_columns],
        )
 
    column_sortable_list = [
        DealOrm.created_at,
        DealOrm.time,
    ]

    name = "Сделка"
    name_plural = "Сделки"
    list_template = "sqladmin/list-logs.html"

    column_default_sort = ("id", "desc")
    column_formatters = {
        DealOrm.created_at: lambda log, _: log.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y %H:%M:%S"
        ),
        DealOrm.time: lambda log, _: log.time.astimezone(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y %H:%M:%S"),
    }
    trader_column_formatters = {
        DealOrm.created_at: lambda log, _: log.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y %H:%M:%S"
        ),
        DealOrm.time: lambda log, _: log.time.astimezone(pytz.timezone("Europe/Moscow")).strftime("%d.%m.%Y %H:%M:%S"),
        DealOrm.operation: lambda log, _: Markup(f'''<span style="color: rgb{operation_colors[log.operation]}">{log.operation}</span>''')
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
                func.extract('epoch', DealOrm.created_at) - func.extract('epoch', DealOrm.time) >= settings.log_delay
            )

        if trader_id:
            filters &= and_(DealOrm.user_id==int(trader_id))
        if start_date:
            filters &= and_(DealOrm.created_at >= datetime.strptime(start_date, "%d.%m.%Y"))
        if end_date:
            filters &= and_(DealOrm.created_at <= datetime.strptime(end_date, "%d.%m.%Y") + timedelta(days=1))

        return filters
    
    
    async def list(self, request: Request) -> Pagination:
        trader_id = request.query_params.get("trader_id")
        self._list_prop_names = self.get_dynamic_list_columns(request)

        if trader_id:
            self._list_formatters = self._build_column_pairs(self.trader_column_formatters)
        else:
            self._list_formatters = self._build_column_pairs(self.column_formatters)

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
