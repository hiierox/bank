import re
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.api.user_data.schemas import (
    GetUserProfileResponse,
    ProductResponse,
    PutUserProfileRequest,
)
from app.core.custom_exceptions import (
    LoanAlreadyExistError,
    LoanNotFoundError,
    UserNotFoundError,
)
from app.dependencies import get_user_data_service
from app.logic.data_service import UserDataService

router = APIRouter()


def validate_phone(phone: str) -> str:
    if not re.fullmatch(r'^7\d{10}$', phone):
        raise HTTPException(status_code=422, detail='Invalid phone format')
    return phone


@router.get('/user-data', response_model=GetUserProfileResponse)
async def get_user_data(
    phone: Annotated[str, Depends(validate_phone)],
    user_data_service: UserDataService = Depends(get_user_data_service)
) -> GetUserProfileResponse:
    try:
        return await user_data_service.get_user_profile(phone)
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        ) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Unexpected error in user_data_service') from e


@router.put('/user-data')
async def put_user_data(
    request: PutUserProfileRequest,
    user_data_service: UserDataService = Depends(
        get_user_data_service)
) -> JSONResponse:
    try:

        is_new_user = await user_data_service.put_user_data(request.phone, request)
        response_body = {'status': 'success'}
        status_code = status.HTTP_201_CREATED if is_new_user else status.HTTP_200_OK
        return JSONResponse(content=response_body, status_code=status_code)

    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        ) from e
    except LoanAlreadyExistError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='Loan already exists'
        ) from e
    except LoanNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Loan not found'
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexpected error in user_data_service'
        ) from e


@router.get('/api/products')
async def get_products_list(
    flow_type: Literal['pioneer', 'repeater'] | None = None,
    user_data_service: UserDataService = Depends(get_user_data_service)
) -> list[ProductResponse] | dict[str, str]:
    try:
        return await user_data_service.get_products_list(flow_type)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Unexcepted error in user_data_service'
        ) from e


@router.get('/metrics')
async def metrics() -> Response:
    """Возвращает метрики Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
