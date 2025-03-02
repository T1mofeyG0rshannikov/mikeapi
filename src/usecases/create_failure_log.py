from fastapi import Request

from src.repositories.log_repository import LogRepository


class CreateFailureLog:
    def __init__(self, log_repository: LogRepository) -> None:
        self.log_repository = log_repository
    
    async def __call__(self, request: Request) -> None:
        body = await request.body()
        body = body.decode()

        await self.log_repository.create_unsuccesslog(body=body)
