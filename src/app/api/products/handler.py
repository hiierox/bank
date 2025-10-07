from typing import Any

from fastapi import APIRouter

from app.logic.flow_service import FlowService
from app.repository.client_repo import ClientRepository
from app.repository.product_repo import ProductRepository

from .schemas import NumberRequest, ResponseModel

client_repo = ClientRepository()
product_repo = ProductRepository()
flow_service = FlowService(client_repo, product_repo)

router = APIRouter()


@router.post('/', response_model=ResponseModel)
async def get_product(request: NumberRequest) -> dict[str, Any]:
    """
    Возвращает клиенту список доступных ему продуктов.
    """
    return await flow_service.flow_type_selection(request.phone_number)
