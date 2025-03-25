from src.entites.trader import StatisticPeriodEnum, StatisticPeriod
from src.db.models.models import TraderStatisticOrm
from markupsafe import Markup
from fastapi.requests import Request

from src.admin.model_views.base import BaseModelView
from sqlalchemy import (
    and_,
    Select
)
from starlette.routing import URLPath
from datetime import datetime, timedelta

DEGREES_COLORS = {
    "more": "(20, 215, 20)",
    "less": "(255, 100, 100)"
}


def format_sum(num: float) -> str:
    num = round(num)
    if abs(num) // 1_000_000 > 0:
        return f"{num // 1_000_000}M"
    if abs(num) // 1_000 > 0:
        return f"{num // 1_000}K"

    return str(num)


def render_degrees(value: int | None) -> str:
    if value is None:
        return ""
    
    if value == 0:
        return ""

    value_format = format_sum(value)

    return f'''<span style="color: rgb{DEGREES_COLORS["more" if value > 0 else "less"]}">({value_format if value < 0 else f"+{value_format}"})</span>'''


class TraderStatisticsAdmin(BaseModelView, model=TraderStatisticOrm):
    column_list = [
        TraderStatisticOrm.end_date,
        TraderStatisticOrm.trader,
    
        TraderStatisticOrm.cash_balance,

        TraderStatisticOrm.stock_balance,
        TraderStatisticOrm.active_lots,

        TraderStatisticOrm.deals,
        
        TraderStatisticOrm.trade_volume,
        TraderStatisticOrm.income,

        TraderStatisticOrm.yield_,
        TraderStatisticOrm.gain,
        TraderStatisticOrm.tickers
    ]
    
    column_sortable_list = [
        TraderStatisticOrm.end_date,
        TraderStatisticOrm.trader,
    
        TraderStatisticOrm.cash_balance,

        TraderStatisticOrm.stock_balance,
        TraderStatisticOrm.active_lots,

        TraderStatisticOrm.deals,
        
        TraderStatisticOrm.trade_volume,
        TraderStatisticOrm.income,

        TraderStatisticOrm.yield_,
        TraderStatisticOrm.gain,
        TraderStatisticOrm.tickers
    ]

    column_formatters = {
        TraderStatisticOrm.end_date: lambda a, _: a.date_value,
        TraderStatisticOrm.trader: lambda a, _: Markup(
            f"""<a href="{URLPath(f'''/admin/trader-statistic-orm/list?trader_id={a.trader_id}''')}">{a.trader}</a>"""
        ),
        TraderStatisticOrm.gain: lambda a, _: Markup(f"{round(a.gain, 2)} % {render_degrees(a.gain_degrees)}"),
        TraderStatisticOrm.trade_volume: lambda a, _: Markup(f"{format_sum(a.trade_volume)} ₽ {render_degrees(a.trade_volume_degrees)}"),
        TraderStatisticOrm.stock_balance: lambda a, _: Markup(f"{format_sum(a.stock_balance)} ₽ {render_degrees(a.stock_balance_degrees)}"),
        TraderStatisticOrm.cash_balance: lambda a, _: Markup(f"{format_sum(a.cash_balance)} ₽ {render_degrees(a.cash_balance_degrees)}"),
        TraderStatisticOrm.income: lambda a, _: Markup(f"{format_sum(a.income)} ₽ {render_degrees(a.income_degrees)}"),
        TraderStatisticOrm.yield_: lambda a, _: Markup(f"{round(a.yield_, 2)} {render_degrees(a.yield_degrees)}"),
        TraderStatisticOrm.deals: lambda a, _: Markup(
            f"""<a href="{URLPath(f'''/admin/log-orm/list?trader_id={a.trader_id}&start_date={a.start_date.strftime("%d.%m.%Y")}&end_date={a.end_date.strftime("%d.%m.%Y")}''')}">{a.deals} {render_degrees(a.deals_degrees)}</a>"""
        ),
    }

    name = "Торговля"
    name_plural = "Торговля"

    column_default_sort = ("end_date", "desc")

    page_size = 100
    
    list_template = "sqladmin/list-traders-statistics.html"
    
    column_labels = {
        "trader": "Трейдер",
        "cash_balance": "Баланс",
        "stock_balance": "Портфель",
        "active_lots": "Лоты",
        "deals": "Сделки",
        "trade_volume": "Оборот",
        "income": "Прибыль",
        "yield_": "Маржа",
        "gain": "Успех",
        "tickers": "Тикеры",
    }
    
    def filters_from_request(self, request: Request) -> Select:
        trader_id = request.query_params.get("trader_id")
        period = request.query_params.get("period", StatisticPeriodEnum.week)

        filters = and_(TraderStatisticOrm.period==period)

        if trader_id:
            filters &= and_(TraderStatisticOrm.trader_id==int(trader_id))
        else:
            filters &= and_(TraderStatisticOrm.end_date >= (datetime.today() - timedelta(days=StatisticPeriod(period).days)).date())
        return filters
