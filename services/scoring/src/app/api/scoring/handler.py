from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.core.custom_exceptions import UserNotFoundError
from app.logic.scoring import UserScoring
from app.repository.client_repo import ClientProfileRepository

from .schemas import ResponseModel, ScoringRequestPioneer, ScoringRequestRepeater

client_repo = ClientProfileRepository()
scoring_service = UserScoring(client_repo)
router = APIRouter()


@router.post('/pioneer', response_model=ResponseModel)
async def get_product_pioneer(request: ScoringRequestPioneer) -> dict[str, Any]:
    return await scoring_service.user_scoring_pioneer(
        user_data=request.user_data,
        products=request.products
    )


@router.post('/repeater', response_model=ResponseModel)
async def get_product_repeater(request: ScoringRequestRepeater) -> dict[str, Any]:
    try:
        return await scoring_service.user_scoring_repeater(
            phone=request.phone,
            products=request.products
        )
    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='User not found') from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='Unexpected error in user_scoring_repeater') from e
