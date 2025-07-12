from dependency_injector import providers, containers
from src.background_tasks.trades_activity import DealsActivity
from src.background_tasks.traders_statistics.traders_statistics import CreateTraderStatistics
from src.background_tasks.tickers_prices import GetTickersPrices
from src.dependencies.repos_container import ReposContainer
from src.background_tasks.tickers_activity import TickersActivity
from src.messaging.sms_sender.config import SMSAeroConfig
from src.messaging.telegram_sender.sender import TelegramSender
from src.messaging.sms_sender.sender import SMSSender
from src.messaging.telegram_sender.config import TelegramSenderConfig
from src.background_tasks.check_server import CheckServer
from src.background_tasks.check_server_config import CheckServerConfig
from src.messaging.alerts_service.config import AlertsServiceConfig
from src.background_tasks.check_server_available import CheckServerActivity
from src.dependencies.base_dependencies import get_redis
from src.messaging.alerts_service.service import AlertsService
from src.usecases.create_usernames import AddUsernames
from src.usecases.create_traders.create_traders import CreateTraders


class Container(containers.Container):
    telegram_config = providers.Singleton(TelegramSenderConfig)
    telegram_sender = providers.Singleton(TelegramSender, config=telegram_config)
    sms_config = providers.Singleton(SMSAeroConfig)
    sms_sender = providers.Singleton(SMSSender, config=sms_config)
    alerts_config = providers.Singleton(AlertsServiceConfig)
    redis = providers.Singleton(get_redis)
    alerts_server = providers.Singleton(AlertsService, config=alerts_config, redis=redis)
    check_server_activity = providers.Factory(CheckServerActivity, 
        repository=ReposContainer.deal_repository,
        scheduler_repository=ReposContainer.scheduler_repository,
        vendor_repository=ReposContainer.vendor_repository,
        telegram_sender=telegram_sender,
        sms_sender=sms_sender,
        alerts_service=alerts_server,
        ping_repository=ReposContainer.ping_repository,
        server_log_repository=ReposContainer.server_log_repository
    )
    check_server_config = providers.Singleton(CheckServerConfig)
    check_server = providers.Factory(CheckServer,
        redis=redis,
        repository=ReposContainer.server_log_repository,
        config=check_server_config
    )
    trader_statistics = providers.Factory(CreateTraderStatistics,
        repository=ReposContainer.trader_repository,
        settings_repository=ReposContainer.settings_repository,
        deal_repository=ReposContainer.deal_repository,
        tickers_repository=ReposContainer.ticker_repository
    )
    add_usernames = providers.Factory(AddUsernames,
        repository=ReposContainer.trader_repository, 
        vendor_repository=ReposContainer.vendor_repository
    )
    create_traders = providers.Factory(CreateTraders,
        traders_repository=ReposContainer.trader_repository
    )
    tickers_activity = providers.Factory(TickersActivity,
        trader_repository=ReposContainer.trader_repository,
        deal_repository=ReposContainer.deal_repository,
        ticker_repository=ReposContainer.ticker_repository
    )
    ticker_prices = providers.Factory(GetTickersPrices,
        deal_repository=ReposContainer.deal_repository,
        settings_repository=ReposContainer.settings_repository,
        ticker_repositpry=ReposContainer.ticker_repository
    )
    deals_activity = providers.Factory(DealsActivity,
        deal_repository=ReposContainer.deal_repository
    )