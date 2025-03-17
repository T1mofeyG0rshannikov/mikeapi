from fastapi import FastAPI

from src.admin.model_views.trader_statistics import TraderStatisticsAdmin
from src.admin.model_views.failure_deal import FailureDealAdmin
from src.admin.model_views.server_log import ServerLogAdmin
from src.admin.model_views.device import VendorAdmin
from src.dependencies.base_dependencies import get_jwt_processor, get_password_hasher
from src.admin.model_views.alerts import AlertsAdmin
from src.admin.model_views.scheduler import SchedulerAdmin
from src.admin.model_views.contacts import ContactAdmin
from src.admin.admin import CustomAdmin
from src.admin.auth import AdminAuth
from src.admin.config import get_admin_config
from src.admin.model_views.ping import PingAdmin
from src.admin.model_views.ticker import TickerAdmin
from src.admin.model_views.trade import LogAdmin
from src.admin.model_views.trader import TraderAdmin
from src.admin.views import (
    APIUrlsAdmin,
    LogActivityAdmin,
    SettingsAdmin,
    UserAdmin,
)
from src.db.database import engine


def init_admin(app: FastAPI):
    authentication_backend = AdminAuth(
        secret_key=get_admin_config().admin_secret_key,
        jwt_processor=get_jwt_processor(),
        password_hasher=get_password_hasher(),
        config=get_admin_config()
    )
    admin = CustomAdmin(
        app=app, engine=engine, authentication_backend=authentication_backend, templates_dir="src/admin/templates"
    )
    admin.add_view(LogActivityAdmin)
    admin.add_view(LogAdmin)
    admin.add_view(TraderAdmin)
    admin.add_view(TickerAdmin)
    admin.add_view(ServerLogAdmin)
    admin.add_view(FailureDealAdmin)
    admin.add_view(PingAdmin)
    admin.add_view(VendorAdmin)
    admin.add_view(APIUrlsAdmin)
    admin.add_view(SchedulerAdmin)
    admin.add_view(ContactAdmin)
    admin.add_view(SettingsAdmin)
    admin.add_view(AlertsAdmin)
    admin.add_view(UserAdmin)
    admin.add_view(TraderStatisticsAdmin)
