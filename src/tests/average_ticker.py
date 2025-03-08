from src.dependencies.dependencies import get_ticker_repository
from src.db.database import get_db
import asyncio
import time

async def get_average_ticker():
    async for db in get_db():
        print("started")
        times = []
        ticker_repository = get_ticker_repository(db)
        tickers = await ticker_repository.all()
        tickers = tickers[0:200] + tickers[-200::]
        
        for ticker in tickers:
            start = time.time()
            await ticker_repository.get(slug=ticker.slug)
            times.append(time.time() - start)
            
        print(sum(times) / len(times))
            

if __name__ == "__main__":
    asyncio.run(get_average_ticker())