import schedule
import time
import asyncio

from src.dependencies.container import Container


async def job() -> None:
    check_server_activity = await Container.check_server_activity()
    await check_server_activity()


def check_server_activity():
    print(time.time())
    asyncio.get_event_loop().run_until_complete(job())

schedule.every(1).minutes.do(check_server_activity)

while True:
    schedule.run_pending()
    time.sleep(1)