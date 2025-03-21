from src.entites.trader import StatisticPeriodEnum
from src.db.models.models import TraderStatisticOrm
from markupsafe import Markup
from fastapi.requests import Request

from src.admin.model_views.base import BaseModelView
from sqlalchemy import (
    and_,
    select,
    func,
    Select
)
from sqladmin.pagination import Pagination
from sqlalchemy.orm import selectinload
from starlette.routing import URLPath


DEGREES_COLORS = {
    "more": "(20, 215, 20)",
    "less": "(255, 100, 100)"
}

def render_degrees(value: int | None) -> str:
    if value is None:
        return ""
    
    if value == 0:
        return ""
    
    if value == int(value):
        value = int(value)
    else:
        value = round(value, 2)

    return f'''<span style="color: rgb{DEGREES_COLORS["more" if value > 0 else "less"]}">({value if value < 0 else f"+{value}"})</span>'''


class TraderStatisticsAdmin(BaseModelView, model=TraderStatisticOrm):
    column_list = [
        TraderStatisticOrm.date_value, 
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
        TraderStatisticOrm.trader: lambda a, _: Markup(
            f"""<a href="{URLPath(f'''/admin/trader-statistic-orm/list?trader_id={a.trader_id}''')}">{a.trader}</a>"""
        ),
        TraderStatisticOrm.gain: lambda a, _: Markup(f"{round(a.gain, 2)} % {render_degrees(a.gain_degrees)}"),
        TraderStatisticOrm.trade_volume: lambda a, _: Markup(f"{round(a.trade_volume)} ₽ {render_degrees(a.trade_volume_degrees)}"),
        TraderStatisticOrm.stock_balance: lambda a, _: Markup(f"{round(a.stock_balance)} ₽ {render_degrees(a.stock_balance_degrees)}"),
        TraderStatisticOrm.cash_balance: lambda a, _: Markup(f"{round(a.cash_balance)} ₽ {render_degrees(a.cash_balance_degrees)}"),
        TraderStatisticOrm.income: lambda a, _: Markup(f"{round(a.income)} ₽ {render_degrees(a.income_degrees)}"),
        TraderStatisticOrm.yield_: lambda a, _: Markup(f"{round(a.yield_, 2)} {render_degrees(a.yield_degrees)}"),
        TraderStatisticOrm.deals: lambda a, _: Markup(
            f"""<a href="{URLPath(f'''/admin/log-orm/list?trader_id={a.trader_id}&start_date={a.start_date.strftime("%d.%m.%Y")}&end_date={a.end_date.strftime("%d.%m.%Y")}''')}">{a.deals} {render_degrees(a.deals_degrees)}</a>"""
        ),
    }

    name = "Торговля"
    name_plural = "Торговля"

    column_default_sort = ("id", "desc")

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

        return filters
    
    async def list(self, request: Request) -> Pagination:
        page = self.validate_page_number(request.query_params.get("page"), 1)
        page_size = self.validate_page_number(request.query_params.get("pageSize"), 0)
        page_size = min(page_size or self.page_size, max(self.page_size_options))

        stmt = self.list_query(request).filter(self.filters_from_request(request))
        for relation in self._list_relations:
            stmt = stmt.options(selectinload(relation))

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
    
    def get_list_value(self, model, column):
        able_types = [int, float]
        try:
            previous = self.previous
        except AttributeError:
            self.previous = model
            return super().get_list_value(model, column)

        if self.previous != model:
            self.previous = model 
        return super().get_list_value(model, column)
