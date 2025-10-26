import asyncio
import json
import logging
from typing import Any

from aiokafka import AIOKafkaConsumer

from app.api.user_data.schemas import LoanEntryItem, PutUserProfileRequest, UserProfile
from app.config.config import KafkaConfig
from app.core.custom_exceptions import LoanAlreadyExistError
from app.logic.data_service import UserDataService

logger = logging.getLogger(__name__)


class KafkaConsumerService:
    def __init__(self, config: KafkaConfig, data_service: UserDataService):
        self.data_service = data_service
        self.consumer = AIOKafkaConsumer(
            config.topic,
            bootstrap_servers=config.bootstrap_servers,
            group_id=config.group_id,
            auto_offset_reset='earliest'
        )
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        """Запускает консьюмер и фоновую задачу по чтению сообщений."""
        logger.info('Starting Kafka consumer...........')
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
        try:
            async for msg in self.consumer:
                try:
                    message_value = json.loads(msg.value.decode('utf-8'))
                    logger.info(
                        f'Получено сообщение key={msg.key} value={message_value}')

                    await self.process_message(message_value)
                    await self.consumer.commit()
                except Exception:
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

        try:
            logger.info(f"Обработка события '{event_type}' под ключу {phone}")
            await self.data_service.put_user_data(phone, request)
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
