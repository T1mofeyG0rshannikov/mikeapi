from typing import Annotated
from fastapi import Depends, Request

from src.dependencies import get_log_repository
from src.repositories.log_repository import LogRepository

'''
async def create_failure_log(
    request: Request,
    log_repository: Annotated[LogRepository, Depends(get_log_repository)]
) -> None:
    body = await request.body()
    body = body.decode()
    print(body)
    await log_repository.create_unsuccesslog(body=body)
    #formatted_string = "\n".join(f"{key} - {value}" for key, value in sorted(body.items()))
    #print(formatted_string)
'''


class CreateFailureLog:
    def __init__(self, log_repository: LogRepository) -> None:
        self.log_repository = log_repository
    
    async def __call__(self, request: Request):
        body = await request.body()
        body = body.decode()

        await self.log_repository.create_unsuccesslog(body=body)
