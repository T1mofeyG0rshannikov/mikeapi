from fastapi import Request
from markupsafe import Markup


from src.admin.model_views.base import BaseModelView
from src.admin.forms import TickerForm
from src.db.models.models import TickerOrm
from src.entites.ticker import TICKER_TYPES
from sqlalchemy import (
    and_,
)


def get_ticker_type_slug(ticker_type: str) -> str:
    for type_ in TICKER_TYPES:
        if type_["value"] == ticker_type:
            return type_.get("slug", "bonds")

    return "bonds"


class TickerAdmin(BaseModelView, model=TickerOrm):
    column_list = [
        TickerOrm.slug,
        TickerOrm.name,
        TickerOrm.type,
        TickerOrm.lot,
        TickerOrm.last_trade_price,
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
    
    def filters_from_request(self, request: Request):
        type = request.query_params.get("type")
        rare = request.query_params.get("rare", False)
        archive = request.query_params.get("archive", False)

        if rare:
            rare = rare == "true"

        if archive:
            archive = archive == "true"

        filters = and_()
        filters &= and_(TickerOrm.archive == archive)
        filters &= and_(TickerOrm.rare == rare)
        
        if type:
            filters &= and_(TickerOrm.type == type)

        return filters

    form = TickerForm

    column_formatters = {
        TickerOrm.slug: lambda ticker, _: Markup(
            f"""<a href="https://www.tbank.ru/invest/{get_ticker_type_slug(ticker.type)}/{ticker.slug}/" target="_blank">{ticker.slug}</a>"""
        ),
        TickerOrm.last_trade_price: lambda ticker, _: f"{ticker.last_trade_price if ticker.last_trade_price else ''} {ticker.currency if ticker.currency else ''}",
    }

    column_details_exclude_list = [TickerOrm.logs]
    form_excluded_columns = [TickerOrm.logs]