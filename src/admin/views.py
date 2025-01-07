from sqladmin import ModelView

from src.admin.forms import APIUrlsCreateForm, UserCreateForm, VendorCreateForm
from src.db.models import APIURLSOrm, LogOrm, UrlEnum, UserOrm, VendorOrm


class LogAdmin(ModelView, model=LogOrm):
    column_list = [LogOrm.id, LogOrm.app, LogOrm.text, LogOrm.time, LogOrm.created_at, LogOrm.main_server]

    name = "Лог"
    name_plural = "Логи"


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
