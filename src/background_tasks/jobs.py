from src.db.database import get_db
from src.dependencies.container import Container

async def trader_activity() -> None:
    async for db in get_db():
        repository= Container.trader_repository(db=db)
        settings_repository= Container.settings_repository(db=db)
        deal_repository= Container.log_repository(db=db)
        
        trader_activity_usecase = Container.trader_activity(
            repository=repository,
            settings_repository=settings_repository,
            deal_repository=deal_repository
        )
        await trader_activity_usecase()


async def check_server() -> None:
    check_server_usecase = await Container.check_server()
    await check_server_usecase()
