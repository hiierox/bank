import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
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
    yield
    await http_client.aclose()


app = FastAPI(lifespan=lifespan)

app.include_router(products_router, prefix='/api/products')
