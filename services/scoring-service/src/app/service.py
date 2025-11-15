import asyncio
import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.scoring.handler import router as scoring_router
from app.api.scoring.health import router as health_router
from app.config.config import settings
from app.external_service.kafka_producer import KafkaProducerService

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
    app.state.http_client = http_client

    kafka_producer = KafkaProducerService(settings)
    app.state.kafka_producer = kafka_producer
    kafta_start_task = asyncio.create_task(start_kafka_with_retries(kafka_producer))

    yield

    kafta_start_task.cancel()
    await kafka_producer.stop()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

app.include_router(scoring_router, prefix='/api/scoring')
app.include_router(health_router)
