from sqladmin import ModelView

from src.admin.forms import UserCreateForm, VendorCreateForm
from src.db.models import APIURLSOrm, LogOrm, TraderOrm, UserOrm, VendorOrm


class LogAdmin(ModelView, model=LogOrm):
    column_list = [LogOrm.id, LogOrm.app, LogOrm.text, LogOrm.time, LogOrm.created_at, LogOrm.main_server]

    name = "Лог"
    name_plural = "Логи"

    column_default_sort = ("created_at", True)
    column_formatters = {LogOrm.created_at: lambda log, _: log.created_at.strftime("%d:%m:%Y.%H:%M:%S")}

    page_size = 100


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

    # form = APIUrlsCreateForm

    name = "url адрес"
    name_plural = "url адреса"


class TraderAdmin(ModelView, model=TraderOrm):
    column_list = [
        TraderOrm.id,
        TraderOrm.username,
        TraderOrm.code,
        TraderOrm.status,
        TraderOrm.subscribes,
        TraderOrm.subscribers,
        TraderOrm.portfolio,
        TraderOrm.trades,
        TraderOrm.profit,
        TraderOrm.badges,
    ]

    list_template = "sqladmin/list.html"

    name = "Трейдер"
    name_plural = "Трейдеры"
