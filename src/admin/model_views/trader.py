import json
import time
import warnings
from collections.abc import AsyncGenerator, Callable, Sequence
from datetime import datetime
from enum import Enum
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Dict,
    List,
    Optional,
    Tuple,
    Type,
    Union,
    no_type_check,
)
from urllib.parse import urlencode

import anyio
import pytz
from fastapi.requests import Request
from markupsafe import Markup
from sqladmin import ModelView, action
from sqladmin._queries import Query
from sqladmin._types import MODEL_ATTR
from sqladmin.ajax import create_ajax_loader
from sqladmin.exceptions import InvalidModelError
from sqladmin.formatters import BASE_FORMATTERS
from sqladmin.forms import ModelConverter, ModelConverterBase, get_model_form
from sqladmin.helpers import (
    Writer,
    get_object_identifier,
    get_primary_keys,
    object_identifier_values,
    prettify_class_name,
    secure_filename,
    slugify_class_name,
    stream_to_csv,
)

# stream_to_csv,
from sqladmin.pagination import Pagination
from sqladmin.templating import Jinja2Templates
from sqlalchemy import (
    Column,
    String,
    and_,
    asc,
    cast,
    delete,
    desc,
    func,
    inspect,
    or_,
    update,
    case
)
from sqlalchemy.exc import NoInspectionAvailable
from sqlalchemy.orm import selectinload, sessionmaker
from sqlalchemy.orm.exc import DetachedInstanceError
from sqlalchemy.sql.elements import ClauseElement
from sqlalchemy.sql.expression import Select, select
from starlette.datastructures import URL
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import RedirectResponse, StreamingResponse
from wtforms import Field, Form
from wtforms.fields.core import UnboundField

from src.db.models.models import TraderOrm, TradersBuffer

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
            buffer = buffer.scalars().first()
            if buffer:
                if buffer.usernames:
                    stmt = select(TraderOrm).where(TraderOrm.username.in_(buffer.usernames))

                    rows = await self._run_query(stmt)
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

            print(parts[-1])
            if parts[-1] == "profit":
                if is_desc:
                    #stmt = stmt.order_by(getattr(model, parts[-1]).isnot(None).desc(), desc(getattr(model, parts[-1])))
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == 0, 1),  # если value == None, то присваиваем 1 (в конце сортировки)
                            else_=0  # иначе присваиваем 0
                        ),
                        getattr(model, parts[-1]).desc())
                else:
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == 0, 1),  # если value == None, то присваиваем 1 (в конце сортировки)
                            else_=0  # иначе присваиваем 0
                        ),
                        getattr(model, parts[-1]).asc())
                    #stmt = stmt.order_by(getattr(model, parts[-1]).isnot(None).desc(), asc(getattr(model, parts[-1])))
            else:
                if is_desc:
                    #stmt = stmt.order_by(getattr(model, parts[-1]).isnot(None).desc(), desc(getattr(model, parts[-1])))
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == None, 1),  # если value == None, то присваиваем 1 (в конце сортировки)
                            else_=0  # иначе присваиваем 0
                        ),
                        getattr(model, parts[-1]).desc())
                else:
                    stmt = stmt.order_by(
                        case(
                            (getattr(model, parts[-1]) == None, 1),  # если value == None, то присваиваем 1 (в конце сортировки)
                            else_=0  # иначе присваиваем 0
                        ),
                        getattr(model, parts[-1]).asc())
                    #stmt = stmt.order_by(getattr(model, parts[-1]).isnot(None).desc(), asc(getattr(model, parts[-1])))

        return stmt

    @action(name="delete_all", label="Удалить все", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            stmt = await self.raw_list(request)
            stmt = await session.execute(stmt)
            stmt = stmt.scalars().all()
            ids = [user.id for user in stmt]
            for i in range(0, len(ids), 5000):
                await session.execute(delete(TraderOrm).where(TraderOrm.id.in_(ids[i : i + 5000])))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    @action(name="add_to_buffer", label="Добавить в буфер все")
    async def add_to_buffer(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            request.url.remove_query_params("pks")
            stmt = await self.raw_list(request)
            rows = await self._run_query(stmt)

            buffer = await session.execute(select(TradersBuffer))
            buffer = buffer.scalars().first()
            if not buffer:
                buffer = TradersBuffer(usernames=[])
                session.add(buffer)
                await session.commit()

            if buffer.usernames is None:
                buffer.usernames = []

            buffer_usernames = list(set(buffer.usernames) | {trader.username for trader in rows})
            buffer.usernames = buffer_usernames

            request.session["buffer_size"] = len(buffer_usernames)

            await session.commit()
            return RedirectResponse(
                url=f"/admin/{slugify_class_name(self.model.__name__)}/list?{request.query_params}", status_code=303
            )

    @action(name="scanned", label="Пометить Scanned")
    async def scanned(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            pks = [int(i) for i in request.query_params.get("pks", "").split(",")]
            await session.execute(update(self.model).where(TraderOrm.id.in_(pks)).values(scanned=True))
            await session.commit()
            return RedirectResponse(
                url=f"/admin/{slugify_class_name(self.model.__name__)}/list?{request.query_params}", status_code=303
            )

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

    async def raw_list(self, request: Request, stmt=None):
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
        subscribers_r = request.query_params.get("subscribers_r")

        badge = request.query_params.get("badge")

        usernames = [username.lower().strip() for username in request.query_params.get("search", "").split(",")]
        usernames = list(filter(lambda x: x, usernames))
        if stmt is None:
            stmt = self.list_query(request)

        if usernames:
            stmt = stmt.filter(func.lower(TraderOrm.username).in_(usernames))

        if badge:
            stmt = stmt.filter(TraderOrm.badges.contains([badge]))

        subscribes_filters = and_()
        if subscribes_l:
            subscribes_filters &= and_(
                int(subscribes_l) <= TraderOrm.subscribes, TraderOrm.subscribes <= int(subscribes_r)
            )
        if subscribes_r:
            subscribes_filters &= and_(TraderOrm.subscribes <= int(subscribes_r))

        stmt = stmt.filter(subscribes_filters)

        subscribers_filters = and_()
        if subscribers_l:
            subscribers_filters &= and_(int(subscribers_l) <= TraderOrm.subscribers)
        if subscribers_r:
            subscribers_filters &= and_(TraderOrm.subscribers <= int(subscribers_r))

        stmt = stmt.filter(subscribers_filters)

        if watch:
            stmt = stmt.filter(TraderOrm.watch == watch)

        profit_filters = and_()
        if profit_l:
            profit_filters &= and_(float(profit_l) <= TraderOrm.profit)
        if profit_r:
            profit_filters &= and_(TraderOrm.profit <= float(profit_r))

        stmt = stmt.filter(profit_filters)

        deals_filters = and_()
        if deals_l:
            deals_filters &= and_(int(deals_l) <= TraderOrm.trades)
        if deals_r:
            deals_filters &= and_(TraderOrm.trades <= int(deals_r))

        stmt = stmt.filter(deals_filters)

        if status:
            stmt = stmt.filter(TraderOrm.status == status)

        if portfolio:
            stmt = stmt.filter(TraderOrm.portfolio == portfolio)

        count_filters = and_()
        if count_l:
            count_filters &= and_(int(count_l) <= TraderOrm.count)
        if count_r:
            count_filters &= and_(TraderOrm.count <= int(count_r))

        stmt = stmt.filter(count_filters)

        for relation in self._list_relations:
            stmt = stmt.options(selectinload(relation))

        if search:
            stmt = self.search_query(stmt=stmt, term=search)

        return stmt

    async def list(self, request: Request) -> Pagination:
        stmt = await self.raw_list(request)
        stmt = self.sort_query(stmt, request)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), self.page_size)
        page = self.validate_page_number(request.query_params.get("page"), 1)

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
