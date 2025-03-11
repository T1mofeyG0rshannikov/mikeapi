from datetime import datetime
from src.background_tasks.check_server_config import CheckServerConfig
from redis import Redis
from src.repositories.server_log_repositrory import ServerLogRepository
import time
import pytz


class CheckServer:
    def __init__(self, redis: Redis, repository: ServerLogRepository, config: CheckServerConfig) -> None:
        self.r = redis
        self.repository = repository
        self.c = config
        
    async def __call__(self) -> None:
        now = datetime.now()
        print(datetime.now(pytz.utc))
        last_available = self.r.get(self.c.ACTIVITY_TIME)
        if last_available is None:
            self.r.set(self.c.ACTIVITY_TIME, int(time.mktime(now.timetuple())))
            return

        last_available = datetime.fromtimestamp(int(self.r.get(self.c.ACTIVITY_TIME)))
        
        diff = (now - last_available).total_seconds()
        if diff > 70:
            await self.repository.create(
                body=f'''Сервер был недоступен с {last_available.strftime("%d.%m.%Y %H:%M:%S")}'''
            )
            
            await self.repository.create(
                body=f'''Сервер возобновил работу в {now.strftime("%d.%m.%Y %H:%M:%S")}'''
            )
            
        self.r.set(self.c.ACTIVITY_TIME, int(time.mktime(now.timetuple())))
        print("activity")
