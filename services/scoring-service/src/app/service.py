import asyncio
import logging
from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response

from app.api.scoring.handler import router as scoring_router
from app.api.scoring.health import router as health_router
from app.config.config import settings
from app.external_service.kafka_producer import KafkaProducerService
from app.external_service.monitoring.metrics import (
    init_service_metrics,
    shutdown_service_metrics,
)
from app.external_service.monitoring.metrics_middleware import metrics_middleware
from app.external_service.monitoring.tracing import setup_tracing

logging.basicConfig(level=logging.INFO)


async def start_kafka_with_retries(kafka_producer: KafkaProducerService) -> None:
    while True:
        try:
            await kafka_producer.start()
            return
        except Exception as e:
            logging.error(f'Kafka connection failed {e}')
            await asyncio.sleep(5)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    http_client = httpx.AsyncClient(
        base_url=settings.DATA_SERVICE_BASE_URL,
        timeout=settings.DATA_SERVICE_TIMEOUT
    )
    init_service_metrics()
    setup_tracing(app)
    app.state.http_client = http_client

    kafka_producer = KafkaProducerService(settings)
    app.state.kafka_producer = kafka_producer
    kafta_start_task = asyncio.create_task(start_kafka_with_retries(kafka_producer))

    yield

    kafta_start_task.cancel()
    await kafka_producer.stop()
    await http_client.aclose()
    shutdown_service_metrics()

app = FastAPI(lifespan=lifespan)

@app.middleware('http')
async def add_prometheus_metrics(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
    """Middleware для сбора метрик."""  # noqa: RUF002
    return await metrics_middleware(request, call_next)

app.include_router(scoring_router, prefix='/api/scoring')
app.include_router(health_router)
