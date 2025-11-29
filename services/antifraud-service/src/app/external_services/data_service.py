import logging

from httpx import AsyncClient, ConnectError, HTTPStatusError, TimeoutException

from app.api.antifraud.schemas import DataServiceResponse
from app.core.exceptions import DataServiceNotFoundError, IntegrationError

logger = logging.getLogger(__name__)

DATA_SERVICE_NAME = 'user-data-service'


class DataService:
    """Сервис для интеграции c user-data-service."""

    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_user_profile(self, phone: str) -> DataServiceResponse:
        """
        Получает профиль пользователя.
        Выбрасывает DataServiceNotFoundError (404) или
        IntegrationError (5xx/Timeout/ConnectError).
        """
        endpoint = f'/user-data?phone={phone}'

        try:
            response = await self.client.get(endpoint)

            if response.status_code == 404:
                logger.error(
                    f'{DATA_SERVICE_NAME} вернул 404 для repeater. endpoint: {endpoint}'
                )
                raise DataServiceNotFoundError(phone)

            response.raise_for_status()

            data = response.json()
            logger.info(f'{DATA_SERVICE_NAME} успешно вернул профиль')
            return DataServiceResponse.model_validate(data)

        except (ConnectError, TimeoutException) as e:
            logger.error(f'{DATA_SERVICE_NAME} connection/timeout error: {e}')
            raise IntegrationError('Connection or timeout error') from e

        except HTTPStatusError as e:
            logger.error(
                f'{DATA_SERVICE_NAME} вернул 5xx. Статус: {e.response.status_code}'
            )
            raise IntegrationError('5xx Error') from e

        except Exception as e:
            logger.error(
                f'Непредвиденная ошибка {DATA_SERVICE_NAME}. Детали: {e}'
            )
            raise IntegrationError from e
