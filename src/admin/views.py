import pytz
from fastapi.requests import Request
from markupsafe import Markup
from sqladmin import ModelView
from sqladmin.pagination import Pagination
from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import select

from src.admin.forms import UserCreateForm, VendorCreateForm
from src.db.models import (
    APIURLSOrm,
    LogActivityOrm,
    LogOrm,
    TraderOrm,
    UserOrm,
    VendorOrm,
)


class LogAdmin(ModelView, model=LogOrm):
    column_list = [
        LogOrm.id,
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

    name = "Лог"
    name_plural = "Логи"

    column_default_sort = ("created_at", True)
    column_formatters = {
        LogOrm.created_at: lambda log, _: log.created_at.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d:%m:%Y.%H:%M:%S"
        )
    }

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
        TraderOrm.app,
    ]

    list_template = "sqladmin/list-traders.html"
    column_labels = {"subscribes": "followers", "subscribers": "watches", "trades": "deals"}
    name = "Трейдер"
    name_plural = "Трейдеры"

    column_sortable_list = ["status"]

    column_formatters = {
        TraderOrm.username: lambda trader, _: Markup(
            f"""<a href="https://www.tbank.ru/invest/social/profile/{trader.username}/" target="_blank">{trader.username}</a>"""
        ),
        TraderOrm.profit: lambda trader, _: f"{trader.profit} %",
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


class LogActivityAdmin(ModelView, model=LogActivityOrm):
    column_list = [
        LogActivityOrm.date,
        LogActivityOrm.hour00,
        LogActivityOrm.hour01,
        LogActivityOrm.hour02,
        LogActivityOrm.hour03,
        LogActivityOrm.hour04,
        LogActivityOrm.hour05,
        LogActivityOrm.hour06,
        LogActivityOrm.hour07,
        LogActivityOrm.hour08,
        LogActivityOrm.hour09,
        LogActivityOrm.hour10,
        LogActivityOrm.hour11,
        LogActivityOrm.hour12,
        LogActivityOrm.hour13,
        LogActivityOrm.hour14,
        LogActivityOrm.hour15,
        LogActivityOrm.hour16,
        LogActivityOrm.hour17,
        LogActivityOrm.hour18,
        LogActivityOrm.hour19,
        LogActivityOrm.hour20,
        LogActivityOrm.hour21,
        LogActivityOrm.hour22,
        LogActivityOrm.hour23,
        LogActivityOrm.last_day,
    ]

    name = "Активность"
    name_plural = "Активность"
    column_labels = {
        "date": "Дата",
        "hour00": "00",
        "hour01": "01",
        "hour02": "02",
        "hour03": "03",
        "hour04": "04",
        "hour05": "05",
        "hour06": "06",
        "hour07": "07",
        "hour08": "08",
        "hour09": "09",
        "hour10": "10",
        "hour11": "11",
        "hour12": "12",
        "hour13": "13",
        "hour14": "14",
        "hour15": "15",
        "hour16": "16",
        "hour17": "17",
        "hour18": "18",
        "hour19": "19",
        "hour20": "20",
        "hour21": "21",
        "hour22": "22",
        "hour23": "23",
        "last_day": "за сутки",
    }

    column_formatters = {
        LogActivityOrm.date: lambda activity, _: activity.date.strftime("%d.%m.%Y"),
    }

    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = False

    page_size = 100

    column_default_sort = ("id", "desc")
