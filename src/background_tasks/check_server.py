from datetime import datetime
from src.dependencies.dependencies import get_server_log_repository
from src.db.database import get_db
from src.dependencies.base_dependencies import get_check_server_config, get_redis
from src.background_tasks.check_server_config import CheckServerConfig
from redis import Redis
from src.repositories.server_log_repositrory import ServerLogRepository
import time


class CheckServer:
    def __init__(self, redis: Redis, repository: ServerLogRepository, config: CheckServerConfig) -> None:
        self.r = redis
        self.repository = repository
        self.c = config
        
    def __call__(self) -> None:
        last_available = self.r.get(self.c.ACTIVITY_TIME)
        if last_available is None:
            self.r.set(self.c.ACTIVITY_TIME, time.mktime(now.timetuple()))
            return

        last_available = datetime.fromtimestamp(int(self.r.get(self.c.ACTIVITY_TIME)))
        now = datetime.now()
        
        diff = (now - last_available).total_seconds()
        if diff > 70:
            self.repository.create(
                body=f'''Сервер был недоступен с {last_available.strftime("%H:%M:%S")} - Сервер возобновил работу в {now.strftime("%H:%M:%S")}'''
            )
            
        self.r.set(self.c.ACTIVITY_TIME, time.mktime(now.timetuple()))
        
import asyncio

async def check_server():
    async for db in get_db():
        redis = get_redis()
        server_log_repository = get_server_log_repository(db)
        check_server_config = get_check_server_config()

        check_server_usecase = CheckServer(
            redis=redis,
            repository=server_log_repository,
            config=check_server_config
        )
        await check_server_usecase()

    
def check_server_job():
    

    asyncio.get_event_loop().run_until_complete(check_server())
