from datetime import datetime
from typing import (
    Any
)

import pytz
from fastapi.requests import Request
from markupsafe import Markup
from sqladmin import action
from sqladmin.helpers import (
    slugify_class_name,
)

from sqlalchemy import (
    and_,
    func,
    update,
    case
)
from sqlalchemy.sql.expression import Select, select
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.admin.model_views.base import BaseModelView
from src.entites.trader import TraderWatch
from src.db.models.models import TraderOrm, TradersBuffer


TRADER_BADGE_ICONS = {
    "Верифицирован": "verified",
    "Автор стратегии": "strategy",
    "Выбор Т-Инвестиции": "choice",
    "Популярный": "popular",
    "Помощник пульса": "assistant",
}


class TraderAdmin(BaseModelView, model=TraderOrm):
    column_list = [
        TraderOrm.watch,
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

    column_export_list = ["username"]

    async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None:
        model.last_update = datetime.utcnow()

    async def get_model_objects(self, request: Request, limit: int | None = 0) -> list[Any]:
        async with self.session_maker(expire_on_commit=False) as session:
            buffer = await session.execute(select(TradersBuffer))
            buffer = buffer.scalar()
            if buffer:
                if buffer.usernames:
                    rows = []
                    for i in range(0, len(buffer.usernames), 5000):
                        traders = await session.execute(select(TraderOrm).where(TraderOrm.username.in_(buffer.usernames[i:i+5000])))
                        traders = traders.scalars().all()
                        rows.extend(traders)

                    return rows
            return []

    def sort_query(self, stmt: Select, request: Request) -> Select:
        """
        A method that is called every time the fields are sorted
        and that can be customized.
        By default, sorting takes place by default fields.

        The 'sortBy' and 'sort' query parameters are available in this request context.
        """
        sort_by = request.query_params.get("sortBy", None)
        sort = request.query_params.get("sort", "asc")

        if sort_by:
            sort_fields = [(sort_by, sort == "desc")]
        else:
            sort_fields = self._get_default_sort()

        for sort_field, is_desc in sort_fields:
            model = self.model

            parts = self._get_prop_name(sort_field).split(".")
            for part in parts[:-1]:
                model = getattr(model, part).mapper.class_
                stmt = stmt.join(model)

            if parts[-1] == "profit":
                if is_desc:
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == 0, 1),
                            else_=0
                        ),
                        getattr(model, parts[-1]).desc())
                else:
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == 0, 1),
                            else_=0
                        ),
                        getattr(model, parts[-1]).asc())
            else:
                if is_desc:
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == None, 1),
                            else_=0
                        ),
                        getattr(model, parts[-1]).desc())
                else:
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == None, 1),
                            else_=0
                        ),
                        getattr(model, parts[-1]).asc())

        return stmt

    @action(name="clear_count", label="Обнулить счетчики популярности")
    async def clear_count_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            query = update(TraderOrm).where(self.filters_from_request(request)).values(count=0)
            await session.execute(query)
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    @action(name="add_to_buffer", label="Добавить в буфер (фильтр)")
    async def add_to_buffer(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            request.url.remove_query_params("pks")
            rows = await self._run_query(self.list_query(request).filter(self.filters_from_request(request)))

            buffer = await session.execute(select(TradersBuffer).limit(1))
            buffer = buffer.scalar()
            if not buffer:
                buffer = TradersBuffer(usernames=[])
                session.add(buffer)
                await session.commit()

            if buffer.usernames is None:
                buffer.usernames = []

            buffer_usernames = list(set(buffer.usernames) | set(trader.username for trader in rows))
            buffer.usernames = buffer_usernames

            request.session["buffer_size"] = len(buffer_usernames)

            await session.commit()
            return RedirectResponse(
                url=f"/admin/{slugify_class_name(self.model.__name__)}/list?{request.query_params}", status_code=303
            )

    @action(name="scanned", label="Scanned (выбранные)")
    async def scanned(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            pks = [int(i) for i in request.query_params.get("pks", "").split(",")]
            await session.execute(update(self.model).where(TraderOrm.id.in_(pks)).values(scanned=True))
            await session.commit()
            return RedirectResponse(
                url=f"/admin/{slugify_class_name(self.model.__name__)}/list?{request.query_params}", status_code=303
            )

    async def _set_status_chosed(self, request: Request, watch: TraderWatch):
        async with self.session_maker(expire_on_commit=False) as session:
            pks = [int(i) for i in request.query_params.get("pks", "").split(",")]
            await session.execute(update(self.model).where(TraderOrm.id.in_(pks)).values(watch=watch))
            await session.commit()
            return RedirectResponse(
                url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303
            )
        
    async def _set_status_filter(self, request: Request, watch: TraderWatch):
        async with self.session_maker(expire_on_commit=False) as session:
            query = update(TraderOrm).where(self.filters_from_request(request)).values(watch=watch)
            await session.execute(query)
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list?{request.query_params}", status_code=303)
            
    @action(name="status_on", label="Статус ON (выбранные)")
    async def status_on(self, request: Request):
        return await self._set_status_chosed(request, watch=TraderWatch.on)
            
    @action(name="status_off_pks", label="Статус OFF (выбранные)")
    async def status_of_pks(self, request: Request):
        return await self._set_status_chosed(request, watch=TraderWatch.off)

    @action(name="status_pre", label="Статус PRE (фильтр)")
    async def status_pre(self, request: Request):
        return await self._set_status_filter(request, watch=TraderWatch.pre)

    @action(name="status_off", label="Статус OFF (фильтр)")
    async def status_off(self, request: Request):
        return await self._set_status_filter(request, watch=TraderWatch.off)
        
    @action(name="status_raw", label="Статус RAW (фильтр)")
    async def status_raw(self, request: Request):
        return await self._set_status_filter(request, watch=TraderWatch.raw)

    column_formatters = {
        TraderOrm.username: lambda trader, _: Markup(
            f"""<a href="https://www.tbank.ru/invest/social/profile/{trader.username}/" target="_blank">{trader.username}</a>"""
        ),
        TraderOrm.profit: lambda trader, _: f"{trader.profit} %" if trader.profit else "0",
        TraderOrm.watch: lambda trader, _: Markup(
            f"""<img width="20" style="min-width: 20px;" height="20" src="/static/icons/ico_{trader.watch}.png" />"""
        ),
        TraderOrm.last_update: lambda trader, _: trader.last_update.astimezone(pytz.timezone("Europe/Moscow")).strftime(
            "%d.%m.%Y"
        )
        if trader.last_update
        else "",
        TraderOrm.badges: lambda trader, _: Markup(
            f'''<div style="display: flex;">{
            "".join([f"""<img style="min-width: 20px; margin-left: -6px; z-index: {100 - ind};" width="20" height="20" src="/static/icons/ico_{TRADER_BADGE_ICONS.get(badge)}.png" />""" for ind, badge in enumerate(trader.badges)])}</div>'''
        )
        if trader.badges
        else "",
        TraderOrm.subscribers: lambda trader, _: Markup(
            f"""<a>{trader.subscribers if trader.subscribers else ""}</a>{'<i style="margin-left: 10px;" class="fa fa-check text-success"></i>' if trader.scanned else ''}"""
        ),
    }

    column_sortable_list = ["portfolio", "trades", "profit", "subscribers", "subscribes", "count", "last_update"]
    
    diapazon_filter_fields = [
        TraderOrm.trades,
        TraderOrm.profit,
        TraderOrm.count,
        TraderOrm.subscribes,
        TraderOrm.subscribers
    ]

    def filters_from_request(self, request: Request):
        filters = super().filters_from_request(request)

        status = request.query_params.get("status")
        portfolio = request.query_params.get("portfolio")
        watch = request.query_params.get("watch")

        badge = request.query_params.get("badge")

        usernames = [username.lower().strip() for username in request.query_params.get("search", "").split(",")]
        usernames = list(filter(lambda x: x, usernames))
        
        if usernames:
            filters &= and_(func.lower(TraderOrm.username).in_(usernames))

        if badge:
            filters &= and_(TraderOrm.badges.contains([badge]))

        if watch:
            filters &= and_(TraderOrm.watch == watch)

        if status:
            filters &= and_(TraderOrm.status == status)

        if portfolio:
            filters &= and_(TraderOrm.portfolio == portfolio)

        return filters
#333 303