from src.entites.trader import StatisticPeriodEnum
from src.db.models.models import TraderStatisticOrm
from markupsafe import Markup
from fastapi.requests import Request

from src.admin.model_views.base import BaseModelView
from datetime import timedelta
from sqlalchemy import (
    and_,
    select,
    func,
    Select
)
from sqladmin.pagination import Pagination
from sqlalchemy.orm import selectinload
from starlette.routing import URLPath


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
        TraderStatisticOrm.gain: lambda a, _: f"{round(a.gain, 2)} %",
        TraderStatisticOrm.trade_volume: lambda a, _: f"{round(a.trade_volume)} ₽",
        TraderStatisticOrm.stock_balance: lambda a, _: f"{round(a.stock_balance)} ₽",
        TraderStatisticOrm.cash_balance: lambda a, _: f"{round(a.cash_balance)} ₽",
        TraderStatisticOrm.income: lambda a, _: f"{round(a.income)} ₽",
        TraderStatisticOrm.yield_: lambda a, _: round(a.yield_, 2),
        TraderStatisticOrm.deals: lambda a, _: Markup(
            f"""<a href="{URLPath(f'''/admin/log-orm/list?trader_id={a.trader_id}&start_date={(a.date-timedelta(a.period_obj.days)).strftime("%d.%m.%Y")}&end_date={a.date.strftime("%d.%m.%Y")}''')}">{a.deals}({a.degrees_deals})</a>"""
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
        #able_types = [int, float]
        #print(rows[0].degrees_deals)
        #for i in range(1, len(rows)):
        #    r=rows[i]
        #    l_r = rows[i - 1]
        #    for c in self.model.__table__.columns:
        #        print(c)
        #        print(getattr(r, str(c).split(".")[1]))
        #        print(type(getattr(r, str(c).split(".")[1])))
        #        print(type(getattr(r, str(c).split(".")[1])) in able_types)
        #        if type(getattr(r, str(c).split(".")[1])) in able_types:
        #            setattr(rows[i], f'''degrees_{str(c).split(".")[1]}''', getattr(r, str(c).split(".")[1]) - getattr(l_r, str(c).split(".")[1]))

        pagination = Pagination(
            rows=rows,
            page=page,
            page_size=page_size,
            count=count,
        )

        return pagination
    
    def get_list_value(self, model, column):
        """
        able_types = [int, float]
        model.degrees_deals=0
        '''for i in range(1, len(rows)):
            r=rows[i]
            l_r = rows[i - 1]
            for c in self.model.__table__.columns:
                print(c)
                print(getattr(r, str(c).split(".")[1]))
                print(type(getattr(r, str(c).split(".")[1])))
                print(type(getattr(r, str(c).split(".")[1])) in able_types)
                if type(getattr(r, str(c).split(".")[1])) in able_types:
                    setattr(rows[i], f'''degrees_{str(c).split(".")[1]}''', getattr(r, str(c).split(".")[1]) - getattr(l_r, str(c).split(".")[1]))
        '''"""
        return super().get_list_value(model, column)  # Важно вызвать super()
