from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from httpx import ConnectError, HTTPStatusError

from app.core.custom_exceptions import LoanAlreadyExistsError, UserNotFoundError
from app.dependencies import get_scoring_service
from app.logic.scoring import UserScoring

from .schemas import ResponseModel, ScoringRequestPioneer, ScoringRequestRepeater

router = APIRouter()


@router.post('/pioneer', response_model=ResponseModel)
async def get_product_pioneer(
        request: ScoringRequestPioneer,
        scoring_service: UserScoring = Depends(get_scoring_service)
) -> dict[str, Any]:
    try:
        return await scoring_service.user_scoring_pioneer(
            user_data=request.user_data,
            products=request.products
        )
    except HTTPStatusError as e:
        raise HTTPException(status_code=502, detail='SavingError') from e
    except ConnectError as e:
        raise HTTPException(status_code=503, detail='ConnectionError') from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail='InternalServerError') from e


@router.post('/repeater', response_model=ResponseModel)
async def get_product_repeater(
    request: ScoringRequestRepeater,
    scoring_service: UserScoring = Depends(
        get_scoring_service)
) -> dict[str, Any]:
    try:
        return await scoring_service.user_scoring_repeater(
            phone=request.phone,
            products=request.products
        )
    except HTTPStatusError as e:
        raise HTTPException(status_code=502, detail='UpdateError') from e
    except ConnectError as e:
        raise HTTPException(status_code=503, detail='ConnectError') from e
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail='UserNotFoundError') from e
    except LoanAlreadyExistsError as e:
        raise HTTPException(status_code=502, detail='LoanAlreadyExistsError') from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail='InternalServerError') from e
