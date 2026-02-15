import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from httpx import AsyncClient
from redis.asyncio.client import Redis

from app.api.antifraud.handler import router as antifraud_router
from app.config.config import settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    redis_client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    http_client = AsyncClient(
        base_url=settings.DATA_SERVICE_BASE_URL,
        timeout=settings.DATA_SERVICE_TIMEOUT
    )
    app.state.redis_client = redis_client
    app.state.http_client = http_client
    logging.info('Успешное создание lifespan')

    yield

    await redis_client.close()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

app.include_router(antifraud_router, prefix='/api/antifraud')
