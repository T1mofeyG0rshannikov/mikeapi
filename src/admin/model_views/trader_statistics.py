from sqladmin import ModelView

from src.db.models.models import TraderStatisticOrm


class TraderStatisticsAdmin(ModelView, model=TraderStatisticOrm):
    column_list = [
        TraderStatisticOrm.date, 
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

    name = "Торговля"
    name_plural = "Торговля"

    column_default_sort = ("id", "desc")

    page_size = 100
