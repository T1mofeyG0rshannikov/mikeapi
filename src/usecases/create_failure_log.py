from fastapi import Request

from src.repositories.deal_repository import DealRepository


class CreateFailureLog:
    def __init__(self, log_repository: DealRepository) -> None:
        self.log_repository = log_repository
    
    async def __call__(self, request: Request) -> None:
        body = await request.body()
        body = body.decode()

        await self.log_repository.create_unsuccesslog(body=body)
