import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.api.user_data.handler import router as user_data_router
from app.api.user_data.health import router as health_router
from app.config.config import settings
from app.external_services.kafka_consumer import KafkaConsumerService
from app.external_services.monitoring.metrics import (
    init_service_metrics,
    shutdown_service_metrics,
)
from app.external_services.monitoring.metrics_middleware import metrics_middleware
from app.external_services.monitoring.tracing import setup_tracing

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logging.info('Starting data-service')
    init_service_metrics()
    setup_tracing(app)
    kafka_consumer = KafkaConsumerService(
        config=settings
    )
    await kafka_consumer.start()

    yield

    logging.info('Shutting down data-service.')
    await kafka_consumer.stop()
    shutdown_service_metrics()

app = FastAPI(lifespan=lifespan)


@app.middleware('http')
async def add_prometheus_metrics(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
    """Middleware для сбора метрик."""  # noqa: RUF002
    return await metrics_middleware(request, call_next)

app.include_router(user_data_router)
app.include_router(health_router)
