from src.dependencies.dependencies import get_trader_repository
from src.db.database import get_db
import asyncio
import time

async def get_average_trader():
    async for db in get_db():
        print("started")
        times = []
        trader_repository = get_trader_repository(db)
        traders = await trader_repository.all()
        traders = traders[0:200] + traders[-200::]
        
        for trader in traders:
            start = time.time()
            await trader_repository.get(username=trader.username)
            times.append(time.time() - start)
            
        print(sum(times) / len(times))
            

if __name__ == "__main__":
    asyncio.run(get_average_trader())