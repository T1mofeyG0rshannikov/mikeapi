from src.dependencies.container import Container


async def check_server() -> None:
    check_server_usecase = await Container.check_server()
    await check_server_usecase()
