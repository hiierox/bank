import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as redis
from fastapi import FastAPI

from app.api.products.handler import router as products_router
from app.api.products.health import router as health_router
from app.config.config import settings

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    http_client = httpx.AsyncClient(
        base_url=settings.DATA_SERVICE_BASE_URL,
        timeout=settings.DATA_SERVICE_TIMEOUT
    )
    app.state.http_client = http_client
    redis_client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        decode_responses=True
    )
    logging.info('Successfully connected to Redis')

    app.state.redis_client = redis_client

    yield
    await redis_client.close()
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(products_router, prefix='/api/products')
app.include_router(health_router)
