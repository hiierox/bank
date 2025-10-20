from unittest.mock import AsyncMock

import pytest

from app.logic.flow_service import FlowService
from app.repository import client_repo, product_repo

MOCK_AVAILABLE_PRODUCTS = [
    {'name': 'Кредит Базовый', 'amount': 'от 10 000 до 20 000', 'percentage': '15%'}
]


@pytest.fixture
def flow_service_fixture():
    mock_client_repo = AsyncMock(spec=client_repo.ClientRepository())
    mock_product_repo = AsyncMock(spec=product_repo.ProductRepository())

    flow_service = FlowService(mock_client_repo, mock_product_repo)

    return flow_service, mock_client_repo, mock_product_repo


@pytest.mark.asyncio
async def test_flow_repeater(flow_service_fixture):
    flow_service, client_repo, product_repo = flow_service_fixture
    phone_number = '79123456789'
    client_repo.is_number_known.return_value = True

    result = await flow_service.flow_type_selection(phone_number)

    assert result['flow_type'] == 'repeater'
    assert result['available_products'] == []


@pytest.mark.asyncio
async def test_flow_pioneer(flow_service_fixture):
    flow_service, client_repo, product_repo = flow_service_fixture
    phone_number = '79123456789'
    client_repo.is_number_known.return_value = False
    product_repo.get_pioneer_products.return_value = MOCK_AVAILABLE_PRODUCTS

    result = await flow_service.flow_type_selection(phone_number)

    assert result['flow_type'] == 'pioneer'
    assert result['available_products'] == MOCK_AVAILABLE_PRODUCTS
    client_repo.add_number.assert_called_once()


@pytest.mark.asyncio
async def test_flow_is_number_known_failure(flow_service_fixture):
    flow_service, client_repo, product_repo = flow_service_fixture
    phone_number = '79123456789'
    client_repo.is_number_known.side_effect = Exception('Database is not available')

    with pytest.raises(Exception):
        await flow_service.flow_type_selection(phone_number)


@pytest.mark.asyncio
async def test_flow_get_pioneer_products_failure(flow_service_fixture):
    flow_service, client_repo, product_repo = flow_service_fixture
    phone_number = '79123456789'
    client_repo.is_number_known.return_value = False
    product_repo.get_pioneer_products.side_effect = Exception(
        'Database is not available'
    )

    with pytest.raises(Exception):
        await flow_service.flow_type_selection(phone_number)
