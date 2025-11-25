from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from opentelemetry import trace

from app.core.custom_exceptions import UserNotFoundError
from app.dependencies import get_scoring_service
from app.logic.scoring import UserScoring

from .schemas import ResponseModel, ScoringRequestPioneer, ScoringRequestRepeater

router = APIRouter()
tracer = trace.get_tracer(__name__)


@router.post('/pioneer', response_model=ResponseModel)
async def get_product_pioneer(
        request: ScoringRequestPioneer,
        scoring_service: UserScoring = Depends(get_scoring_service)
) -> dict[str, Any]:
    with tracer.start_as_current_span('/api/scoring/pioneer') as span:
        span.set_attribute('http.method', 'POST')
        span.set_attribute('user.phone_prefix', request.phone[:4])
        try:
            return await scoring_service.user_scoring_pioneer(
                user_data=request.user_data,
                products=request.products
            )
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(
                status_code=500, detail='InternalServerError') from e


@router.post('/repeater', response_model=ResponseModel)
async def get_product_repeater(
    request: ScoringRequestRepeater,
    scoring_service: UserScoring = Depends(
        get_scoring_service)
) -> dict[str, Any]:
    with tracer.start_as_current_span('/api/scoring/repeater') as span:
        span.set_attribute('http.method', 'POST')
        span.set_attribute('user.phone_prefix', request.phone[:4])
        try:
            return await scoring_service.user_scoring_repeater(
                phone=request.phone,
                products=request.products
            )
        except UserNotFoundError as e:
            span.record_exception(e)
            raise HTTPException(status_code=404, detail='UserNotFoundError') from e
        except Exception as e:
            span.record_exception(e)
            raise HTTPException(
                status_code=500, detail='InternalServerError') from e
