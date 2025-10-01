from fastapi import APIRouter
from .schemas import NumberRequest, ResponseModel
from app.repository.client_repo import ClientRepository
from app.repository.product_repo import ProductRepository
from app.logic.flow_service import FlowService

client_repo = ClientRepository()
product_repo = ProductRepository()
flow_service = FlowService(client_repo, product_repo)

router = APIRouter()


@router.post("/", response_model=ResponseModel)
async def get_product(request: NumberRequest):
    result = await flow_service.flow_type_selection(request.phone_number)
    return result
