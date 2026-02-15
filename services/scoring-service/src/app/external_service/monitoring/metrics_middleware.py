import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from contextvars import ContextVar

from fastapi import Request, Response

from app.external_service.monitoring.metrics import (
    SERVICE_NAME,
    http_request_duration_seconds,
    http_requests_total,
)

logger = logging.getLogger(__name__)
request_id_var: ContextVar[str] = ContextVar[str]('request_id', default='system')


def generate_request_id() -> str:
    """Генерирует короткий request_id в формате: a73e1a9820058365."""
    return uuid.uuid4().hex[:16]


async def metrics_middleware(
          request: Request, call_next: Callable[[Request], Awaitable[Response]]
        ) -> Response:
    """
    Middleware для сбора метрик Rate, Errors, Duration для HTTP запросов.
    """  # noqa: RUF002

    request_id = request_id_var.get()
    if request_id == 'system':
        request_id = generate_request_id()
        request_id_var.set(request_id)

    extra = {'request_id': request_id}

    logger.info(f'Входящий запрос: {request.method} {request.url.path}', extra=extra)
    extra = {'request_id': request_id}

    start_time = time.time()

    path = request.url.path
    method = request.method

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    except Exception as e:
        logger.error(f'Ошибка обработки запроса: {e}', extra=extra, exc_info=True)
        status_code = 500
        raise e
    finally:
            duration = time.time() - start_time
            http_requests_total.labels(
                method=method, endpoint=path, status=status_code, service=SERVICE_NAME
            ).inc()

            http_request_duration_seconds.labels(
                method=method, endpoint=path, service=SERVICE_NAME
            ).observe(time.time() - start_time)
            logger.info(
            f'Запрос обработан: {request.method} {request.url.path} - '
            f'status={status_code} duration={duration:.3f}s',
            extra=extra
        )
