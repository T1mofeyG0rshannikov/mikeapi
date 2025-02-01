import pytz
from fastapi.requests import Request
from markupsafe import Markup
from sqladmin import ModelView, action
from sqladmin.helpers import slugify_class_name
from sqladmin.pagination import Pagination
from sqlalchemy import and_, delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import select
from starlette.responses import RedirectResponse

from src.db.models.models import TraderOrm

TRADER_BADGE_ICONS = {
    "Верифицирован": "verified",
    "Автор стратегии": "strategy",
    "Выбор Т-Инвестиций": "choice",
    "Популярный": "popular",
    "Помощник пульса": "assistant",
}


class TraderAdmin(ModelView, model=TraderOrm):
    column_list = [
        TraderOrm.badges,
        TraderOrm.id,
        TraderOrm.username,
        TraderOrm.code,
        TraderOrm.status,
        TraderOrm.portfolio,
        TraderOrm.trades,
        TraderOrm.profit,
        TraderOrm.subscribers,
        TraderOrm.subscribes,
        TraderOrm.watch,
        TraderOrm.count,
        TraderOrm.last_update,
        TraderOrm.app,
    ]

    page_size = 100
    list_template = "sqladmin/list-traders.html"
    column_labels = {
        "count": "N",
        "last_update": "Update",
        "id": "ID",
        "badges": "Badges",
        "username": "Username",
        "code": "Code",
        "status": "Status",
        "subscribes": "followers",
        "subscribers": "watch",
        "trades": "deals",
        "watch": "",
    }
    name = "Трейдер"
    name_plural = "Трейдеры"

    column_default_sort = ("id", "desc")

    @action(name="delete_all", label="Удалить все", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            await session.execute(delete(self.model))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    column_formatters = {
        TraderOrm.username: lambda trader, _: Markup(
            f"""<a href="https://www.tbank.ru/invest/social/profile/{trader.username}/" target="_blank">{trader.username}</a>"""
        ),
        TraderOrm.profit: lambda trader, _: f"{trader.profit} %" if trader.profit else "",
        TraderOrm.watch: lambda trader, _: Markup(
            f"""<img width="20" style="min-width: 20px;" height="20" src="/static/icons/ico_{trader.watch}.png" />"""
        ),
        TraderOrm.last_update: lambda trader, _: trader.last_update.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y"
        )
        if trader.last_update
        else "",
        TraderOrm.badges: lambda trader, _: Markup(
            f'''<div style="display: flex; gap: 10px;">{
            "".join([f"""<img style="min-width: 20px;" width="20" height="20" src="/static/icons/ico_{TRADER_BADGE_ICONS.get(badge)}.png" />""" for badge in trader.badges])}</div>'''
        )
        if trader.badges
        else "",
    }

    column_sortable_list = ["portfolio", "trades", "profit", "subscribers", "subscribes", "count", "last_update"]

    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))
        search = request.query_params.get("search", None)
        status = request.query_params.get("status")
        portfolio = request.query_params.get("portfolio")
        deals_l = request.query_params.get("deals_l")
        deals_r = request.query_params.get("deals_r")
        profit_l = request.query_params.get("profit_l")
        profit_r = request.query_params.get("profit_r")
        watch = request.query_params.get("watch")

        count_l = request.query_params.get("count_l")
        count_r = request.query_params.get("count_r")

        subscribes_l = request.query_params.get("subscribes_l")
        subscribes_r = request.query_params.get("subscribes_r")

        subscribers_l = request.query_params.get("subscribers_l")
        subscribers_r = request.query_params.get("subscribes_r")

        badge = request.query_params.get("badge")

        usernames = [username.lower().strip() for username in request.query_params.get("search", "").split(",")]
        usernames = list(filter(lambda x: x, usernames))

        stmt = self.list_query(request)
        if usernames:
            print(usernames, "usernames")
            stmt = stmt.filter(func.lower(TraderOrm.username).in_(usernames))

        if badge:
            stmt = stmt.filter(TraderOrm.badges.contains([badge]))

        if subscribes_l:
            stmt = stmt.filter(
                and_(int(subscribes_l) <= TraderOrm.subscribes, TraderOrm.subscribes <= int(subscribes_r))
            )

        if subscribers_l:
            stmt = stmt.filter(
                and_(int(subscribers_l) <= TraderOrm.subscribers, TraderOrm.subscribers <= int(subscribers_r))
            )

        if watch:
            stmt = stmt.filter(TraderOrm.watch == watch)

        if profit_l:
            stmt = stmt.filter(and_(float(profit_l) <= TraderOrm.profit, TraderOrm.profit <= float(profit_r)))

        if deals_l:
            stmt = stmt.filter(and_(int(deals_l) <= TraderOrm.trades, TraderOrm.trades <= int(deals_r)))

        if status:
            stmt = stmt.filter(TraderOrm.status == status)

        if portfolio:
            stmt = stmt.filter(TraderOrm.portfolio == portfolio)

        if count_l:
            stmt = stmt.filter(and_(int(count_l) <= TraderOrm.count, TraderOrm.count <= int(count_r)))

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
