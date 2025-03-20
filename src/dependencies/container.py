from dependency_injector import containers, providers
from src.repositories.user_repository import UserRepository
from src.background_tasks.traders_statistics import CreateTraderStatistics, TraderStatistics
from src.messaging.sms_sender.config import SMSAeroConfig
from src.messaging.telegram_sender.sender import TelegramSender
from src.messaging.sms_sender.sender import SMSSender
from src.messaging.telegram_sender.config import TelegramSenderConfig
from src.repositories.settings_repository import SettingsRepository
from src.repositories.ticker_repository import TickerRepository
from src.repositories.trader_repository import TraderRepository
from src.background_tasks.check_server import CheckServer
from src.background_tasks.check_server_config import CheckServerConfig
from src.alerts_service.config import AlertsServiceConfig
from src.repositories.server_log_repositrory import ServerLogRepository
from src.repositories.ping_repository import PingRepository
from src.repositories.scheduler_repository import SchedulerRepository
from src.repositories.vendor_repository import VendorRepository
from src.repositories.log_repository import LogRepository
from src.background_tasks.check_server_available import CheckServerActivity
from src.db.database import get_db
from src.dependencies.base_dependencies import get_redis
from src.alerts_service.service import AlertsService


class Container(containers.Container):
    db = providers.Resource(get_db)
    log_repository = providers.Factory(LogRepository, db=db)
    vendor_repository = providers.Factory(VendorRepository, db=db)
    ticker_repository = providers.Factory(TickerRepository, db=db)
    trader_repository = providers.Factory(TraderRepository, db=db)
    user_repository = providers.Factory(UserRepository, db=db)
    telegram_config = providers.Singleton(TelegramSenderConfig)
    telegram_sender = providers.Singleton(TelegramSender, config=telegram_config)
    sms_config = providers.Singleton(SMSAeroConfig)
    sms_sender = providers.Singleton(SMSSender, config=sms_config)
    alerts_config = providers.Singleton(AlertsServiceConfig)
    redis = providers.Singleton(get_redis)
    alerts_server = providers.Singleton(AlertsService, config=alerts_config, redis=redis)
    ping_repository = providers.Factory(PingRepository, db=db)
    server_log_repository = providers.Factory(ServerLogRepository, db=db)
    scheduler_repository = providers.Factory(SchedulerRepository, db=db)
    settings_repository = providers.Factory(SettingsRepository, db=db)
    check_server_activity = providers.Factory(CheckServerActivity, 
        repository=log_repository,
        scheduler_repository=scheduler_repository,
        vendor_repository=vendor_repository,
        telegram_sender=telegram_sender,
        sms_sender=sms_sender,
        alerts_service=alerts_server,
        ping_repository=ping_repository,
        server_log_repository=server_log_repository
    )
    check_server_config = providers.Singleton(CheckServerConfig)
    check_server = providers.Factory(CheckServer,
        redis=redis,
        repository=server_log_repository,
        config=check_server_config
    )
    create_trader_statistics = providers.Factory(CreateTraderStatistics,
        repository=trader_repository, 
        deal_repository=log_repository,
    )
    trader_statistics = providers.Factory(TraderStatistics,
        settings_repository=settings_repository,
        create_statistics=create_trader_statistics    
    )