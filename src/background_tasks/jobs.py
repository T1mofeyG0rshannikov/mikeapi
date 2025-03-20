from src.db.database import get_db
from src.dependencies.container import Container

async def trader_activity() -> None:
    async for db in get_db():
        repository = Container.trader_repository(db=db)
        settings_repository = Container.settings_repository(db=db)
        deal_repository = Container.log_repository(db=db)
        
        create_trader_statistics = Container.create_trader_statistics(
            repository=repository,
            deal_repository=deal_repository
        )

        trader_activity_usecase = Container.trader_statistics(
            settings_repository=settings_repository,
            create_statistics=create_trader_statistics,
            trader_repository=repository
        )
        await trader_activity_usecase()


async def check_server() -> None:
    check_server_usecase = await Container.check_server()
    await check_server_usecase()
