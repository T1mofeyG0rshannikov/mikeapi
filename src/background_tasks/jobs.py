from src.dependencies.repos_container import ReposContainer
from src.db.database import db_generator
from src.dependencies.container import Container


async def trader_activity() -> None:
    async for db in db_generator():
        usecase = Container.trader_statistics(
            repository=ReposContainer.trader_repository(db=db),
            settings_repository=ReposContainer.settings_repository(db=db),
            deal_repository=ReposContainer.deal_repository(db=db),
            tickers_repository=ReposContainer.ticker_repository(db=db)
        )
        await usecase()


async def check_server() -> None:
    async for db in db_generator():
        usecase = Container.check_server(
            repository=ReposContainer.server_log_repository(db=db)
        )
        await usecase()


async def tickers_activity() -> None:
    async for db in db_generator():
        usecase = Container.tickers_activity(
            trader_repository=ReposContainer.trader_repository(db=db),
            deal_repository=ReposContainer.deal_repository(db=db),
            ticker_repository=ReposContainer.ticker_repository(db=db)
        )
        await usecase()


async def ticker_prices() -> None:
    async for db in db_generator():
        usecase = Container.ticker_prices(
            deal_repository=ReposContainer.deal_repository(db=db),
            settings_repository=ReposContainer.settings_repository(db=db),
            ticker_repositpry=ReposContainer.ticker_repository(db=db)
        )
        await usecase()
        print("calculated ticker prices")


async def deals_activity() -> None:
    async for db in db_generator():
        usecase = Container.deals_activity(
            deal_repository=ReposContainer.deal_repository(db=db)
        )
        await usecase()