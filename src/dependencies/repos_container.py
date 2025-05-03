from dependency_injector import containers, providers
from src.repositories.user_repository import UserRepository
from src.repositories.settings_repository import SettingsRepository
from src.repositories.ticker_repository import TickerRepository
from src.repositories.trader_repository import TraderRepository
from src.repositories.server_log_repositrory import ServerLogRepository
from src.repositories.ping_repository import PingRepository
from src.repositories.scheduler_repository import SchedulerRepository
from src.repositories.vendor_repository import DeviceRepository
from src.repositories.deal_repository import DealRepository
from src.db.database import db_generator


class ReposContainer(containers.Container):
    db = providers.Resource(db_generator)
    deal_repository = providers.Factory(DealRepository, db=db)
    vendor_repository = providers.Factory(DeviceRepository, db=db)
    ticker_repository = providers.Factory(TickerRepository, db=db)
    trader_repository = providers.Factory(TraderRepository, db=db)
    user_repository = providers.Factory(UserRepository, db=db)
   
    ping_repository = providers.Factory(PingRepository, db=db)
    server_log_repository = providers.Factory(ServerLogRepository, db=db)
    scheduler_repository = providers.Factory(SchedulerRepository, db=db)
    settings_repository = providers.Factory(SettingsRepository, db=db)
