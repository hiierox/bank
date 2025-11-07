from typing import cast

import httpx
import redis.asyncio as redis
from fastapi import Depends, Request

from app.external_services.redis import RedisService
from app.logic.flow_service import FlowService


def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)


def get_redis_client(request: Request) -> redis.Redis:
    return cast(redis.Redis, request.app.state.redis_client)


def get_redis_service(
        redis_client: redis.Redis = Depends(get_redis_client),
) -> RedisService:
    return RedisService(redis_client=redis_client)


def get_flow_service(
    client: httpx.AsyncClient = Depends(get_http_client),
    redis_service: RedisService = Depends(get_redis_service)
) -> FlowService:
    return FlowService(
        client=client,
        redis_service=redis_service
    )
