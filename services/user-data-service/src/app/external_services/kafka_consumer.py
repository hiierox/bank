import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer
from opentelemetry.semconv._incubating.attributes.messaging_attributes import (
    MESSAGING_DESTINATION_NAME,
    MESSAGING_KAFKA_MESSAGE_KEY,
    MESSAGING_SYSTEM,
)
from opentelemetry.trace import SpanKind

from app.api.user_data.schemas import LoanEntryItem, PutUserProfileRequest, UserProfile
from app.config.config import Settings
from app.core.custom_exceptions import LoanAlreadyExistError
from app.database.database import async_session_maker
from app.external_services.monitoring.tracing import get_kafka_propagator, get_tracer
from app.logic.data_service import UserDataService

logger = logging.getLogger(__name__)
tracer = get_tracer()
propagator = get_kafka_propagator()

class KafkaConsumerService:
    def __init__(self, config: Settings):
        self.consumer = AIOKafkaConsumer(
            config.KAFKA_TOPIC,
            bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
            group_id=config.KAFKA_GROUP_ID,
            auto_offset_reset='earliest'
        )
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Запускает консьюмер и фоновую задачу по чтению сообщений."""
        logger.info('Starting Kafka consumer...........')
        with tracer.start_as_current_span('kafka.consumer.start.wrapper'):
            await self.consumer.start()
        self._task = asyncio.create_task(self.consume())
        logger.info('Kafka consumer started.')

    async def stop(self) -> None:
        """Останавливает консьюмер."""
        logger.info('Stopping Kafka consumer...........')
        if self._task:
            self._task.cancel()
        await self.consumer.stop()
        logger.info('Kafka consumer stopped.')

    async def consume(self) -> None:
        """Бесконечный цикл, который читает и обрабатывает сообщения из Kafka."""
        logger.info('консьюмер начал принимать.')

        try:
            async for msg in self.consumer:
                carrier = {k.decode('utf-8'): v.decode('utf-8') for k, v in msg.headers}
                context = propagator.extract(carrier)
                logger.info('Проходимся по сообщениям')

                with tracer.start_as_current_span(
                    f'{msg.topic} process',
                    context=context,
                    kind=SpanKind.CONSUMER
                ) as span:
                    logger.info('зашли в спан')
                    span.set_attribute(MESSAGING_SYSTEM, 'kafka')
                    span.set_attribute(MESSAGING_DESTINATION_NAME, msg.topic)
                    span.set_attribute(
                        MESSAGING_KAFKA_MESSAGE_KEY, msg.key.decode('utf-8')
                    )
                    try:

                        message_value = json.loads(msg.value.decode('utf-8'))
                        logger.info(
                            f'Получено сообщение key={msg.key} value={message_value}')

                        await self.process_message(message_value)
                        await self.consumer.commit()
                    except Exception as e:
                        span.record_exception(e)
                        logger.exception(
                            f'Ошибка обработки сообщения: {msg.value}')
        except asyncio.CancelledError:
            logger.info('Задача консьюмера остановлена.')
        finally:
            logger.info('Цикл консьюмера завершен')

    async def process_message(self, message: dict[str, Any]) -> None:
        """Валидирует и обрабатывает одно сообщение из Kafka."""

        if message.get('version') != 1:
            logger.warning(
                f"Неподдерживаемая версия сообщения: {message.get('version')}."
            )
            return
        event_type = message.get('event')
        phone = message.get('phone')
        profile_dict = message.get('profile')
        history_dict = message.get('history_entry')

        if not isinstance(phone, str):
            logger.error(f'Телефон не строка: {message}.')
            return
        if not all([event_type, phone, history_dict]):
            logger.error(f'Остутствует обязательное поле: {message}')
            return

        try:
            loan_entry = LoanEntryItem.model_validate(history_dict)
            profile = UserProfile.model_validate(
                profile_dict) if profile_dict else None

            request = PutUserProfileRequest(
                phone=phone,
                profile=profile,
                loan_entry=loan_entry
            )
        except Exception as e:
            logger.exception(
                f'Pydantic валидация провалена: {message}. Error: {e}')
            return

        async with async_session_maker() as session:
            data_service = UserDataService(session)
            try:
                logger.info(
                    f"Обработка события '{event_type}' под ключу {phone}"
                )
                await data_service.put_user_data(phone, request)
                logger.info(f'Обработка успешно завершена для ключа {phone}')

            except LoanAlreadyExistError:
                logger.warning(
                    f'Кредит c id {loan_entry.loan_id} уже существует {phone}.'
                )
            except Exception:
                logger.exception(
                    f"""Ошибка сохранения данных для {phone}.
                    Сообщение будет обработано повторно"""
                )
                raise
