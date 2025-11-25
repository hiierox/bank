from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from httpx import ConnectError, HTTPStatusError
from opentelemetry import trace

from app.dependencies import get_flow_service
from app.logic.flow_service import FlowService

from .schemas import NumberRequest, ResponseModel

router = APIRouter()
tracer = trace.get_tracer(__name__)


@router.post('/', response_model=ResponseModel)
async def get_product(
    request: NumberRequest,
    flow_service: FlowService = Depends(get_flow_service)
) -> dict[str, Any]:
    """
    Возвращает клиенту список доступных ему продуктов
    """
    with tracer.start_as_current_span('/api/products') as span:
        span.set_attribute('http.method', 'PUT')
        span.set_attribute('user.phone_prefix', request.phone_number[:4])
        try:
            return await flow_service.flow_type_selection(request.phone_number)
        except HTTPStatusError as e:
            span.record_exception(e)
            raise HTTPException(status_code=502, detail='Integration Error') from e
        except ConnectError as e:
            span.record_exception(e)
            raise HTTPException(status_code=503, detail='Connect Error') from e
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(status_code=500, detail='Internal Server Error') from e
