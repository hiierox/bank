import logging
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from app.config.config import settings
from app.external_services.monitoring.metrics import (
    external_service_calls_total,
)
from app.external_services.redis import RedisService

logger = logging.getLogger(__name__)


class FlowService:
    def __init__(
        self,
        client: httpx.AsyncClient,
        redis_service: RedisService
    ):
        self.client = client
        self.redis_service = redis_service
        self.retryer = AsyncRetrying(
            stop=stop_after_attempt(
                settings.DATA_SERVICE_MAX_ATTEMPTS + 1
            ),
            wait=wait_fixed(settings.DATA_SERVICE_DELAY),
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
        status_code = '500'
        try:
            response = await self.client.get(f'/user-data?phone={phone}')
            status_code = str(response.status_code)
        except httpx.RequestError:
            status_code = 'error'
        finally:
            external_service_calls_total.labels(
                service_name='user-data-service-kbatrakov',
                method='GET',
                endpoint='/user-data',
                status=status_code
            ).inc()
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
        except Exception as e:
            logger.error(
                f'Integration error with user-data-service. phone={phone}, {str(e)}'  # noqa: RUF010
                )
            raise e

        if flow_type is None:
            logger.error('Flow type selection Error')
            raise Exception

        products = await self.redis_service.get_products(flow_type)

        if products is None:
            status_code = '500'
            try:
                response = await self.client.get(f'/api/products?flow_type={flow_type}')
                response.raise_for_status()
                products = response.json()
            except httpx.RequestError:
                status_code = 'error'
            finally:
                external_service_calls_total.labels(
                    service_name='user-data-service-kbatrakov',
                    method='GET',
                    endpoint='/api/products',
                    status=status_code
                )
            await self.redis_service.set_products(flow_type, products) # type: ignore [arg-type]

        return {
            'flow_type': flow_type,
            'available_products': products
        }
