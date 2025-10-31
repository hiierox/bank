import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.api.user_data.handler import router as user_data_router
from app.config.config import Config
from app.external_services.kafka_consumer import KafkaConsumerService

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    logging.info('Starting data-service')

    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    config = Config.from_yaml(config_path)


    kafka_consumer = KafkaConsumerService(
        config=config.kafka,
    )
    await kafka_consumer.start()

    yield

    logging.info('Shutting down data-service.')
    await kafka_consumer.stop()

app = FastAPI(lifespan=lifespan)

app.include_router(user_data_router)
