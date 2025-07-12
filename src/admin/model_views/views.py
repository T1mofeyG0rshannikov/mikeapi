from sqladmin import ModelView

from src.admin.model_views.base import BaseModelView
from src.admin.forms import UserCreateForm
from src.db.models.models import (
    APIURLSOrm,
    LogActivityOrm,
    SettingsOrm,
    UserOrm
)


class UserAdmin(ModelView, model=UserOrm):
    column_list = [UserOrm.id, UserOrm.username, UserOrm.email, UserOrm.is_superuser]

    form = UserCreateForm

    name = "Пользователь"
    name_plural = "Пользователи"


class APIUrlsAdmin(ModelView, model=APIURLSOrm):
    column_list = [APIURLSOrm.main_url, APIURLSOrm.reverse_url]

    name = "API шлюз"
    name_plural = "API шлюзы"


class LogActivityAdmin(BaseModelView, model=LogActivityOrm):
    column_list = [
        LogActivityOrm.date,
        LogActivityOrm.hour00,
        LogActivityOrm.hour01,
        LogActivityOrm.hour02,
        LogActivityOrm.hour03,
        LogActivityOrm.hour04,
        LogActivityOrm.hour05,
        LogActivityOrm.hour06,
        LogActivityOrm.hour07,
        LogActivityOrm.hour08,
        LogActivityOrm.hour09,
        LogActivityOrm.hour10,
        LogActivityOrm.hour11,
        LogActivityOrm.hour12,
        LogActivityOrm.hour13,
        LogActivityOrm.hour14,
        LogActivityOrm.hour15,
        LogActivityOrm.hour16,
        LogActivityOrm.hour17,
        LogActivityOrm.hour18,
        LogActivityOrm.hour19,
        LogActivityOrm.hour20,
        LogActivityOrm.hour21,
        LogActivityOrm.hour22,
        LogActivityOrm.hour23,
        LogActivityOrm.last_day,
    ]

    list_template = "sqladmin/list-activity.html"
    name = "Активность"
    name_plural = "Активность"
    column_labels = {
        "date": "Дата",
        "hour00": "00",
        "hour01": "01",
        "hour02": "02",
        "hour03": "03",
        "hour04": "04",
        "hour05": "05",
        "hour06": "06",
        "hour07": "07",
        "hour08": "08",
        "hour09": "09",
        "hour10": "10",
        "hour11": "11",
        "hour12": "12",
        "hour13": "13",
        "hour14": "14",
        "hour15": "15",
        "hour16": "16",
        "hour17": "17",
        "hour18": "18",
        "hour19": "19",
        "hour20": "20",
        "hour21": "21",
        "hour22": "22",
        "hour23": "23",
        "last_day": "за сутки",
    }

    column_formatters = {
        LogActivityOrm.date: lambda activity, _: activity.date.strftime("%d.%m.%Y"),
    }

    can_create = False
    can_delete = False
    can_edit = False
    can_view_details = False
    can_export = False

    page_size = 100

    column_default_sort = ("id", "desc")


class SettingsAdmin(ModelView, model=SettingsOrm):
    column_list = [SettingsOrm.log_delay, SettingsOrm.rare_tickers_limit]

    name = "Настройки"
    name_plural = "Настройки"
