from typing import Any

from fastapi import APIRouter

from app.logic.scoring import UserScoring
from app.repository.client_repo import ClientProfileRepository

from .schemas import ResponseModel, ScoringRequest

client_repo = ClientProfileRepository()
scoring_service = UserScoring(client_repo)
router = APIRouter()


@router.post('/', response_model=ResponseModel)
async def get_product(request: ScoringRequest) -> dict[str, Any]:
    return await scoring_service.user_scoring(user_data=request.user_data,
                                           products=request.products)
