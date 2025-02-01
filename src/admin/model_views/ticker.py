from fastapi import Request
from fastapi.responses import RedirectResponse
from markupsafe import Markup
from sqladmin import ModelView, action
from sqladmin.helpers import slugify_class_name
from sqladmin.pagination import Pagination
from sqlalchemy import delete, func, select
from sqlalchemy.orm import selectinload

from src.admin.forms import TickerForm
from src.db.models.models import TickerOrm
from src.entites.ticker import TICKER_TYPES


def get_ticker_type_slug(ticker_type: str) -> str:
    for type_ in TICKER_TYPES:
        if type_["value"] == ticker_type:
            return type_.get("slug", "bonds")

    return "bonds"


class TickerAdmin(ModelView, model=TickerOrm):
    column_list = [
        TickerOrm.slug,
        TickerOrm.name,
        TickerOrm.type,
        TickerOrm.lot,
        TickerOrm.last_trade_price,
        # TickerOrm.currency,
        TickerOrm.end,
        TickerOrm.last_hour,
        TickerOrm.last_hour_traders,
        TickerOrm.last_day,
        TickerOrm.last_day_traders,
        TickerOrm.last_week,
        TickerOrm.last_week_traders,
        TickerOrm.last_month,
        TickerOrm.last_month_traders,
        TickerOrm.trades,
        TickerOrm.traders,
    ]

    name = "Тикер"
    name_plural = "Тикеры"

    can_export = False
    page_size = 100

    column_default_sort = "slug"

    column_sortable_list = [
        TickerOrm.slug,
        TickerOrm.name,
        TickerOrm.type,
        TickerOrm.lot,
        TickerOrm.last_trade_price,
        TickerOrm.last_hour,
        TickerOrm.last_hour_traders,
        TickerOrm.last_day,
        TickerOrm.last_day_traders,
        TickerOrm.last_week,
        TickerOrm.last_week_traders,
        TickerOrm.last_month,
        TickerOrm.last_month_traders,
        TickerOrm.trades,
        TickerOrm.traders,
    ]

    list_template = "sqladmin/list-tickers.html"

    column_labels = {
        "slug": "Тикер",
        "name": "название",
        "lot": "Лот",
        "currency": "Валюта",
        "trades": "Всего(с)",
        "last_trade_price": "Цена",
        "last_hour": "1ч(с)",
        "last_hour_traders": "1ч(т)",
        "last_day": "1д(с)",
        "last_day_traders": "1д(т)",
        "last_week": "1н(с)",
        "last_week_traders": "1н(т)",
        "last_month": "1м(с)",
        "last_month_traders": "1м(т)",
        "traders": "Всего(т)",
        "end": "Конец",
    }

    @action(name="delete_all", label="Удалить все", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            await session.execute(delete(self.model))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))
        search = request.query_params.get("search", None)
        type = request.query_params.get("type")
        rare = request.query_params.get("rare", False)
        if rare:
            if rare == "true":
                rare = True
            else:
                rare = False

        archive = request.query_params.get("archive", False)
        if archive:
            if archive == "true":
                archive = True
            else:
                archive = False

        stmt = self.list_query(request)
        stmt = stmt.filter(TickerOrm.archive == archive)
        stmt = stmt.filter(TickerOrm.rare == rare)

        if type:
            stmt = stmt.filter(TickerOrm.type == type)

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

    form = TickerForm

    column_formatters = {
        TickerOrm.slug: lambda ticker, _: Markup(
            f"""<a href="https://www.tbank.ru/invest/{get_ticker_type_slug(ticker.type)}/{ticker.slug}/" target="_blank">{ticker.slug}</a>"""
        ),
        TickerOrm.last_trade_price: lambda ticker, _: f"{ticker.last_trade_price if ticker.last_trade_price else ''} {ticker.currency if ticker.currency else ''}",
    }
