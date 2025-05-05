from src.dependencies.repos_container import ReposContainer
from src.repositories.deal_repository import DealRepository
from time import time
import asyncio

async def get_lots_deals():
    start = time()
    deal_repository: DealRepository = await ReposContainer.deal_repository()
    print("start")
    
    await deal_repository.update_many({"adopted": False, "adopted_device_id": None})
    
    print(time() - start)


if __name__ == "__main__":
    asyncio.run(get_lots_deals())