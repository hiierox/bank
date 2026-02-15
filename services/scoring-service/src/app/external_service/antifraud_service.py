import logging
from typing import Any

from httpx import AsyncClient, ConnectError, HTTPStatusError, TimeoutException

from app.api.scoring.schemas import UserData, UserDataFromDataService
from app.core.custom_exceptions import IntegrationError

logger = logging.getLogger(__name__)

ANTIFRAUD_SERVICE_NAME = 'antifraud-service'


class AntifraudService:
    def __init__(self, client: AsyncClient):
        self.client = client

    async def check_pioneer(self, user_data: UserData) -> Any:
        """Отправляет запрос на проверку pioneer."""
        endpoint = '/api/antifraud/pioneer/check'
        request_data = {'user_data': user_data.model_dump(mode='json')}

        try:
            response = await self.client.post(endpoint, json=request_data)
            response.raise_for_status()

            return response.json()

        except (ConnectError, TimeoutException) as e:
            logger.error(f'{ANTIFRAUD_SERVICE_NAME} connection/timeout error: {e}')
            raise IntegrationError('Connection or timeout error') from e

        except HTTPStatusError as e:
            logger.error(
                f'{ANTIFRAUD_SERVICE_NAME} вернул 5xx. Статус: {e.response.status_code}'
            )
            raise IntegrationError('5xx Error') from e


    async def check_repeater(
        self, phone: str, new_updated_profile: UserDataFromDataService
    ) -> Any:
        """Отправляет запрос на проверку repeater."""
        endpoint = '/api/antifraud/repeater/check'
        request_data = {
            'phone': phone,
            'new_updated_profile': new_updated_profile.model_dump(mode='json'),
        }

        try:
            response = await self.client.post(endpoint, json=request_data)
            response.raise_for_status()

            return response.json()

        except (ConnectError, TimeoutException) as e:
            logger.error(f'{ANTIFRAUD_SERVICE_NAME} connection/timeout error: {e}')
            raise IntegrationError('Connection or timeout error') from e

        except HTTPStatusError as e:
            logger.error(
                f'{ANTIFRAUD_SERVICE_NAME} вернул 5xx. Статус: {e.response.status_code}'
            )
            raise IntegrationError('5xx Error') from e
