from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from httpx import ConnectError, HTTPStatusError

from app.dependencies import get_flow_service
from app.logic.flow_service import FlowService

from .schemas import NumberRequest, ResponseModel

router = APIRouter()


@router.post('/', response_model=ResponseModel)
async def get_product(
    request: NumberRequest,
    flow_service: FlowService = Depends(get_flow_service)
) -> dict[str, Any]:
    """
    Возвращает клиенту список доступных ему продуктов.
    """
    try:
        return await flow_service.flow_type_selection(request.phone_number)
    except HTTPStatusError as e:
        raise HTTPException(status_code=502, detail='Integration Error') from e
    except ConnectError as e:
        raise HTTPException(status_code=503, detail='Connect Error') from e
    except Exception as e:
        raise HTTPException(status_code=500, detail='Internal Server Error') from e
