from src.admin.model_views.base import BaseModelView
from src.db.models.models import TickerPriceOrm


class TickerPriceAdmin(BaseModelView, model=TickerPriceOrm):
    column_list = [TickerPriceOrm.ticker, TickerPriceOrm.date, TickerPriceOrm.price]

    name = "Цена тикера"
    name_plural = "Цены тикеров"
