import logging
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from app.config.config import Config
from app.repository.product_repo import ProductRepository

logger = logging.getLogger(__name__)


class FlowService:
    def __init__(self, product_repo: ProductRepository,
                 client: httpx.AsyncClient,
                 config: Config
                 ):
        self.product_repo = product_repo
        self.client = client
        self.retryer = AsyncRetrying(
            stop=stop_after_attempt(
                config.data_service.retries.max_attempts + 1
            ),
            wait=wait_fixed(config.data_service.retries.delay),
            retry=retry_if_exception_type(
                (httpx.TimeoutException, httpx.HTTPStatusError)
            ),
            reraise=True
        )

    async def check_client_type(self, phone: str) -> str | None:
        """
        Делает запрос к data-service c ретраями
        Возвращает тип клиента или выбрасывает исключение
        """
        response = await self.client.get(f'/user-data?phone={phone}')
        if response.status_code == 200:
            return 'repeater'
        elif response.status_code == 404:  # noqa: RET505
            return 'pioneer'
        else:
            logger.error(
                f"""Error checking client type:
                    phone={phone},
                    tatus_code={response.status_code},
                    detail={response.text}"""
            )
            response.raise_for_status()
        return None

    async def flow_type_selection(self, phone: str) -> dict[str, Any]:
        """
        Определение типа флоу для клиента и возврат подходящих данных
        """
        try:
            flow_type = None
            async for attempt in self.retryer:
                with attempt:
                    flow_type = await self.check_client_type(phone)
            if flow_type == 'repeater':
                products = await self.product_repo.get_repeater_products()
            if flow_type == 'pioneer':
                products = await self.product_repo.get_pioneer_products()
            return {
                'flow_type': flow_type,
                'available_products': products
            }
        except Exception as e:
            logger.error(
                f'Integration error with user-data-service. phone={phone}, {str(e)}'  # noqa: RUF010
                )
            raise e
