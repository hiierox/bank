import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer
from aiokafka.errors import KafkaError
from opentelemetry.semconv._incubating.attributes.messaging_attributes import (
    MESSAGING_DESTINATION_NAME,
    MESSAGING_KAFKA_MESSAGE_KEY,
    MESSAGING_SYSTEM,
)
from opentelemetry.trace import SpanKind

from app.config.config import Settings
from app.external_service.monitoring.tracing import get_kafka_propagator, get_tracer

logger = logging.getLogger(__name__)

tracer = get_tracer()
propagator = get_kafka_propagator()


class KafkaProducerService:
    def __init__(self, config: Settings):
        self.config = config
        self.producer = AIOKafkaProducer(
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            request_timeout_ms=config.KAFKA_TIMEOUT_MS
        )
        self.topic = self.config.KAFKA_TOPIC

    async def start(self) -> None:
        logger.info('Starting Kafka producer...')
        await self.producer.start()
        logger.info('Kafka producer started.')

    async def stop(self) -> None:
        logger.info('Stopping Kafka producer...')
        await self.producer.stop()

    async def send(self, key: str, value: dict[str, Any]) -> None:
        """Отправляет сообщение в топик"""
        headers: dict[str, str] = {}
        with tracer.start_as_current_span(
            f'{self.topic} send', kind=SpanKind.PRODUCER
        ) as span:
            span.set_attribute(MESSAGING_SYSTEM, 'kafka')
            span.set_attribute(MESSAGING_DESTINATION_NAME, self.topic)
            span.set_attribute(MESSAGING_KAFKA_MESSAGE_KEY, key)

            propagator.inject(headers)
            kafka_headers = [
                (k, v.encode('utf-8')) for k, v in headers.items()
                ]

            logger.info(f'Отправка сообщения в кафку c ключом {key}')
            try:
                value_bytes = json.dumps(value, default=str).encode('utf-8')
                key_bytes = key.encode('utf-8')

                await self.producer.send_and_wait(
                    topic=self.topic,
                    value=value_bytes,
                    key=key_bytes,
                    headers=kafka_headers
                )
            except KafkaError as e:
                span.record_exception(e)
                logger.exception(f'Ошибка отправки сообщения в кафку c ключом {key}')
                raise

        logger.info(f'Сообщение c ключом {key} отправлено в кафку')
