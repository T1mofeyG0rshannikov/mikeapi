import pytz
from fastapi.requests import Request
from markupsafe import Markup
from sqladmin import ModelView, action
from sqladmin.helpers import slugify_class_name
from sqladmin.pagination import Pagination
from sqlalchemy import delete, func
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.expression import select
from starlette.responses import RedirectResponse

from src.db.models import TraderOrm

TRADER_BADGE_ICONS = {
    "Верифицирован": "verified",
    "Автор стратегии": "strategy",
    "Выбор Т-Инвестиций": "choice",
    "Популярный": "popular",
    "Помощник пульса": "assistant",
}


class TraderAdmin(ModelView, model=TraderOrm):
    column_list = [
        TraderOrm.watch,
        TraderOrm.badges,
        TraderOrm.id,
        TraderOrm.username,
        TraderOrm.code,
        TraderOrm.subscribers,
        TraderOrm.subscribes,
        TraderOrm.portfolio,
        TraderOrm.trades,
        TraderOrm.status,
        TraderOrm.profit,
        TraderOrm.last_update,
        TraderOrm.count,
        TraderOrm.app,
    ]

    page_size = 100
    list_template = "sqladmin/list-traders.html"
    column_labels = {"subscribes": "followers", "subscribers": "watches", "trades": "deals"}
    name = "Трейдер"
    name_plural = "Трейдеры"

    column_sortable_list = ["status", "portfolio"]
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
        TraderOrm.profit: lambda trader, _: f"{trader.profit} %" if trader.profit else "-",
        TraderOrm.watch: lambda trader, _: Markup(
            f"""<img width="20" height="20" src="/static/icons/ico_{trader.watch}.png" />"""
        ),
        TraderOrm.last_update: lambda trader, _: trader.last_update.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d:%m:%Y.%H:%M:%S"
        )
        if trader.last_update
        else "-",
        TraderOrm.badges: lambda trader, _: Markup(
            f'''<div style="display: flex; gap: 10px;">{
            "".join([f"""<img width="20" height="20" src="/static/icons/ico_{TRADER_BADGE_ICONS.get(badge)}.png" />""" for badge in trader.badges])}</div>'''
        )
        if trader.badges
        else "-",
    }

    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))
        search = request.query_params.get("search", None)
        status = request.query_params.get("status")
        portfolio = request.query_params.get("portfolio")
        trades = request.query_params.get("trades")
        profit = request.query_params.get("profit")
        profit_degres = request.query_params.get("profitDegres")
        watch = request.query_params.get("watch")

        subscribes = request.query_params.get("subscribes")
        subscribes_degres = request.query_params.get("subscribesDegres")

        subscribers = request.query_params.get("subscribers")
        subscribers_degres = request.query_params.get("subscribesDegrers")

        badge = request.query_params.get("badge")

        stmt = self.list_query(request)

        if badge:
            stmt = stmt.filter(TraderOrm.badges.contains([badge]))

        if subscribes:
            if subscribes_degres == "g":
                stmt = stmt.filter(TraderOrm.subscribes >= int(subscribes))
            elif subscribes_degres == "l":
                stmt = stmt.filter(TraderOrm.subscribes <= int(subscribes))

        if subscribers:
            if subscribers_degres == "g":
                stmt = stmt.filter(TraderOrm.subscribers >= int(subscribers))
            elif subscribers_degres == "l":
                stmt = stmt.filter(TraderOrm.subscribers <= int(subscribers))

        if watch:
            stmt = stmt.filter(TraderOrm.watch == watch)

        if profit:
            if profit_degres == "g":
                stmt = stmt.filter(TraderOrm.profit >= float(profit))
            elif profit_degres == "l":
                stmt = stmt.filter(TraderOrm.profit <= float(profit))

        if trades:
            stmt = stmt.filter(TraderOrm.trades >= int(trades))

        if status:
            stmt = stmt.filter(TraderOrm.status == status)

        if portfolio:
            stmt = stmt.filter(TraderOrm.portfolio == portfolio)

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
