import pytz
from fastapi.requests import Request
from sqladmin import ModelView, action
from sqladmin.helpers import (
    slugify_class_name,
)

from sqladmin.pagination import Pagination
from sqlalchemy import (
    delete,
    select,
)
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import select
from starlette.requests import Request
from starlette.responses import RedirectResponse
from sqlalchemy import func
from src.db.models.models import LogOrm


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
            stmt = await self.raw_list(request)
            stmt = await session.execute(stmt)
            stmt = stmt.scalars().all()
            ids = [user.id for user in stmt]
            for i in range(0, len(ids), 5000):
                await session.execute(delete(self.model).where(self.model.id.in_(ids[i : i + 5000])))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    page_size = 100
    can_export = False

    async def raw_list(self, request: Request):
        search = request.query_params.get("search", None)
        delayed = request.query_params.get("delayed", False)

        if delayed == "true":
            delayed = True
        if delayed == "false":
            delayed = False
            
        stmt = self.list_query(request)
        
        if delayed:
            stmt = stmt.filter(LogOrm.delayed == delayed)

        for relation in self._list_relations:
            stmt = stmt.options(selectinload(relation))

        if search:
            stmt = self.search_query(stmt=stmt, term=search)

        return stmt

    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))

        stmt = await self.raw_list(request)

        stmt = self.sort_query(stmt, request)

        count = await self.count(request, select(func.count()).select_from(stmt))

        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        rows = await self._run_query(stmt)

        pagination = Pagination(
            rows=rows,
            page=page,
            page_size=page_size,
            count=count,
        )

        return pagination
