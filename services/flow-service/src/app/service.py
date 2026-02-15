import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as redis
from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.api.products.handler import router as products_router
from app.api.products.health import router as health_router
from app.config.config import settings
from app.external_services.monitoring.metrics import (
    init_service_metrics,
    shutdown_service_metrics,
)
from app.external_services.monitoring.metrics_middleware import metrics_middleware
from app.external_services.monitoring.tracing import setup_tracing

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    http_client = httpx.AsyncClient(
        base_url=settings.DATA_SERVICE_BASE_URL,
        timeout=settings.DATA_SERVICE_TIMEOUT
    )
    app.state.http_client = http_client
    init_service_metrics()
    setup_tracing(app)
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
    shutdown_service_metrics()


app = FastAPI(lifespan=lifespan)

@app.middleware('http')
async def add_prometheus_metrics(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
    """Middleware для сбора метрик."""  # noqa: RUF002
    return await metrics_middleware(request, call_next)

app.include_router(products_router, prefix='/api/products')
app.include_router(health_router)
