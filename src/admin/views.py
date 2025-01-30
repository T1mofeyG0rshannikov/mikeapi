import pytz
from fastapi.requests import Request
from sqladmin import ModelView, action
from sqladmin.helpers import slugify_class_name
from sqlalchemy import delete
from starlette.responses import RedirectResponse

from src.admin.forms import UserCreateForm, VendorCreateForm
from src.db.models import (
    APIURLSOrm,
    LogActivityOrm,
    LogOrm,
    SettingsOrm,
    UserOrm,
    VendorOrm,
)


class UserAdmin(ModelView, model=UserOrm):
    column_list = [UserOrm.id, UserOrm.username, UserOrm.email, UserOrm.is_superuser]

    form = UserCreateForm

    name = "Пользователь"
    name_plural = "Пользователи"


class VendorAdmin(ModelView, model=VendorOrm):
    column_list = [VendorOrm.app_id, VendorOrm.auth_token]

    form = VendorCreateForm

    name = "Приложение"
    name_plural = "Приложения"


class APIUrlsAdmin(ModelView, model=APIURLSOrm):
    column_list = [APIURLSOrm.main_url, APIURLSOrm.reverse_url]

    name = "url адрес"
    name_plural = "url адреса"


class LogActivityAdmin(ModelView, model=LogActivityOrm):
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

    @action(name="delete_all", label="Удалить все", confirmation_message="Вы уверены?")
    async def delete_all_action(self, request: Request):
        async with self.session_maker(expire_on_commit=False) as session:
            await session.execute(delete(self.model))
            await session.commit()
            return RedirectResponse(url=f"/admin/{slugify_class_name(self.model.__name__)}/list", status_code=303)

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
