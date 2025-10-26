import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError

from app.config.config import KafkaConfig

logger = logging.getLogger(__name__)


class KafkaProducerService:
    def __init__(self, kafka_config: KafkaConfig):
        self.kafka_config = kafka_config
        self.producer = AIOKafkaProducer(
            bootstrap_servers=kafka_config.bootstrap_servers,
            request_timeout_ms=kafka_config.request_timeout_ms
        )
        self.topic = self.kafka_config.topic

    async def start(self) -> None:
        logger.info('Starting Kafka producer...')
        await self.producer.start()
        logger.info('Kafka producer started.')

    async def stop(self) -> None:
        logger.info('Stopping Kafka producer...')
        await self.producer.stop()

    async def send(self, key: str, value: dict[str, Any]) -> None:
        """Отправляет сообщение в топик"""
        logger.info(f'Отправка сообщения в кафку c ключом {key}')
        try:
            value_bytes = json.dumps(value, default=str).encode('utf-8')
            key_bytes = key.encode('utf-8')

            await self.producer.send_and_wait(
                topic=self.topic,
                value=value_bytes,
                key=key_bytes
            )
        except KafkaError:

            logger.exception(f'Ошибка отправки сообщения в кафку c ключом {key}')

        logger.info(f'Сообщение c ключом {key} отправлено в кафку')
