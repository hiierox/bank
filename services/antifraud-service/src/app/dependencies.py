from typing import cast

from fastapi import Depends, Request
from httpx import AsyncClient
from redis.asyncio.client import Redis

from app.external_services.data_service.logic.data_service import DataService
from app.external_services.redis_service.redis_service import RedisService
from app.logic.antifraud_logic import AntifraudService


def get_redis_client(request: Request) -> Redis:
    return cast(Redis, request.app.state.redis_client)

def get_http_client(request: Request) -> AsyncClient:
    return cast(AsyncClient, request.app.state.http_client)

def get_redis_service(redis_client: Redis = Depends(get_redis_client)) -> RedisService:
    return RedisService(redis_client)

def get_data_service(
        httpx_client: AsyncClient = Depends(get_http_client)
        ) -> DataService:
    return DataService(httpx_client)

def get_antifraud_service(
    data_service: DataService = Depends(get_data_service),
    redis_service: RedisService = Depends(get_redis_service)
) -> AntifraudService:
    return AntifraudService(data_service=data_service, redis_service=redis_service)
