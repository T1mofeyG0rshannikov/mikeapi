from fastapi.requests import Request
from markupsafe import Markup
from sqladmin import ModelView
from sqladmin.pagination import Pagination
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import select

from src.admin.forms import UserCreateForm, VendorCreateForm
from src.db.models import APIURLSOrm, LogOrm, TraderOrm, UserOrm, VendorOrm


class LogAdmin(ModelView, model=LogOrm):
    column_list = [
        LogOrm.id,
        LogOrm.app,
        LogOrm.text,
        LogOrm.time,
        LogOrm.user,
        LogOrm.price,
        LogOrm.currency,
        LogOrm.operation,
        LogOrm.ticker,
        LogOrm.created_at,
        LogOrm.main_server,
    ]

    name = "Лог"
    name_plural = "Логи"

    column_default_sort = ("created_at", True)
    column_formatters = {LogOrm.created_at: lambda log, _: log.created_at.strftime("%d:%m:%Y.%H:%M:%S")}

    page_size = 100


class UserAdmin(ModelView, model=UserOrm):
    column_list = [UserOrm.id, UserOrm.username, UserOrm.email, UserOrm.is_superuser]

    form = UserCreateForm

    name = "Пользователь"
    name_plural = "Пользователи"


class VendorAdmin(ModelView, model=VendorOrm):
    column_list = [VendorOrm.app_id, VendorOrm.auth_token]

    form = VendorCreateForm

    name = "Приложение"
    name_plural = "Приложения"


class APIUrlsAdmin(ModelView, model=APIURLSOrm):
    column_list = [APIURLSOrm.main_url, APIURLSOrm.reverse_url]

    name = "url адрес"
    name_plural = "url адреса"


class TraderAdmin(ModelView, model=TraderOrm):
    column_list = [
        TraderOrm.id,
        TraderOrm.username,
        TraderOrm.code,
        TraderOrm.status,
        TraderOrm.subscribes,
        TraderOrm.subscribers,
        TraderOrm.portfolio,
        TraderOrm.trades,
        TraderOrm.profit,
        TraderOrm.badges,
        TraderOrm.watch,
        TraderOrm.count,
    ]

    list_template = "sqladmin/list-traders.html"

    name = "Трейдер"
    name_plural = "Трейдеры"

    column_sortable_list = ["status"]

    column_formatters = {
        TraderOrm.username: lambda trader, _: Markup(
            f"""<a href="https://www.tbank.ru/invest/social/profile/{trader.username}/" target="_blank">{trader.username}</a>"""
        )
    }

    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))
        search = request.query_params.get("search", None)
        status = request.query_params.get("status")

        stmt = self.list_query(request)

        if status:
            stmt = stmt.filter(TraderOrm.status == status)

        for relation in self._list_relations:
            stmt = stmt.options(selectinload(relation))

        stmt = self.sort_query(stmt, request)

        if search:
            stmt = self.search_query(stmt=stmt, term=search)
            count = await self.count(request, select(func.count()).select_from(stmt))
        else:
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
