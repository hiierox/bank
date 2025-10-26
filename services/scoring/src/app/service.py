import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api.scoring.handler import router as scoring_router
from app.dependencies import get_config
from app.external_service.kafka_producer import KafkaProducerService

logging.basicConfig(level=logging.INFO)
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config = get_config()
    http_client = httpx.AsyncClient(
        base_url=config.data_service.base_url,
        timeout=config.data_service.timeout
    )
    app.state.http_client = http_client

    kafka_producer = KafkaProducerService(config.kafka)
    await kafka_producer.start()
    app.state.kafka_producer = kafka_producer

    yield

    await kafka_producer.stop()
    await http_client.aclose()

app = FastAPI(lifespan=lifespan)

app.include_router(scoring_router, prefix='/api/scoring')
