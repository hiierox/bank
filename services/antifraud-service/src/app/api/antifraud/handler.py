from fastapi import APIRouter, Depends, HTTPException, status

from app.api.antifraud.schemas import (
    AntifraudDecisionResponse,
    PioneerCheckRequest,
    RepeaterCheckRequest,
)
from app.core.exceptions import DataServiceNotFoundError, IntegrationError
from app.dependencies import get_antifraud_service
from app.logic.antifraud_logic import AntifraudService

router = APIRouter()


@router.post(
    '/pioneer/check', response_model=AntifraudDecisionResponse,
    status_code=status.HTTP_200_OK
)
async def check_pioneer(
    request: PioneerCheckRequest,
    antifraud_service: AntifraudService = Depends(get_antifraud_service),
) -> AntifraudDecisionResponse:
    """Антифрод проверка для pioneer"""
    try:
        return await antifraud_service.check_pioneer(request)
    except IntegrationError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail='Integration Error'
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal Server Error',
        ) from e


@router.post(
    '/repeater/check', response_model=AntifraudDecisionResponse,
    status_code=status.HTTP_200_OK
)
async def check_repeater(
    request: RepeaterCheckRequest,
    antifraud_service: AntifraudService = Depends(get_antifraud_service),
) -> AntifraudDecisionResponse:
    """Антифрод проверка для repeater"""
    try:
        return await antifraud_service.check_repeater(request)
    except (IntegrationError, DataServiceNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY, detail='Integration Error'
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='Internal Server Error',
        ) from e
