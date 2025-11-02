import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as redis
from fastapi import FastAPI

from app.api.products.handler import router as products_router
from app.dependencies import get_config

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config = get_config()
    http_client = httpx.AsyncClient(
        base_url=config.data_service.base_url,
        timeout=config.data_service.timeout
    )
    app.state.http_client = http_client
    redis_client = redis.Redis(
        host=config.redis.host,
        port=config.redis.port,
        decode_responses=True
    )
    logging.info('Successfully connected to Redis')

    app.state.redis_client = redis_client

    yield
    await redis_client.close()
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(products_router, prefix='/api/products')
