from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.config.config import Config
from app.logic.flow_service import FlowService
from app.repository.product_repo import PIONEER_PRODUCTS, REPEATER_PRODUCTS


@pytest.fixture
def config_fixture() -> Config:
    return Config.model_validate({
        'data_service': {
            'base_url': 'test_url',
            'timeout': 1,
            'retries': {'max_attempts': 2, 'delay': 0}
        }
    })


@pytest.fixture
def flow_service_fixture(config_fixture):
    mock_http_client = AsyncMock(spec=httpx.AsyncClient)
    mock_product_repo = AsyncMock()
    mock_http_response = MagicMock(spec=httpx.Response)

    mock_product_repo.get_pioneer_products.return_value = PIONEER_PRODUCTS
    mock_product_repo.get_repeater_products.return_value = REPEATER_PRODUCTS

    service = FlowService(
        product_repo=mock_product_repo,
        client=mock_http_client,
        config=config_fixture
    )
    return service, mock_http_client, mock_http_response


@pytest.mark.asyncio
async def test_check_client_type_repeater(flow_service_fixture):
    flow_service, mock_client, mock_response = flow_service_fixture
    phone = '79123456789'
    mock_response.status_code = 200
    mock_client.get.return_value = mock_response

    result = await flow_service.check_client_type(phone)

    assert result == 'repeater'


@pytest.mark.asyncio
async def test_check_client_type_pioneer(flow_service_fixture):
    flow_service, mock_client, mock_response = flow_service_fixture
    phone = '79123456789'
    mock_response.status_code = 404
    mock_client.get.return_value = mock_response

    result = await flow_service.check_client_type(phone)

    assert result == 'pioneer'


@pytest.mark.asyncio
async def test_check_client_type_exception_raised(flow_service_fixture):
    flow_service, mock_client, mock_response = flow_service_fixture
    phone = '79123456789'

    mock_response.status_code = 500
    http_error = httpx.HTTPStatusError(
        'Server Error',
        request=MagicMock(spec=httpx.Request),
        response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_client.get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        await flow_service.check_client_type(phone)


@pytest.mark.asyncio
async def test_flow_selection_repeater_success(flow_service_fixture):
    flow_service, mock_client, mock_response = flow_service_fixture
    phone_number = '79123456789'

    mock_response.status_code = 200
    mock_client.get.return_value = mock_response

    result = await flow_service.flow_type_selection(phone_number)

    mock_client.get.assert_called_once_with(f'/user-data?phone={phone_number}')
    assert result['flow_type'] == 'repeater'
    assert result['available_products'] == REPEATER_PRODUCTS


@pytest.mark.asyncio
async def test_flow_selection_pioneer_success(flow_service_fixture):
    flow_service, mock_client, mock_response = flow_service_fixture
    phone_number = '79123456789'

    mock_response.status_code = 404
    mock_client.get.return_value = mock_response

    result = await flow_service.flow_type_selection(phone_number)

    mock_client.get.assert_called_once_with(f'/user-data?phone={phone_number}')
    assert result['flow_type'] == 'pioneer'
    assert result['available_products'] == PIONEER_PRODUCTS


@pytest.mark.asyncio
async def test_flow_selection_exception_raised(flow_service_fixture):
    flow_service, mock_client, mock_response = flow_service_fixture
    phone_number = '79123456789'

    mock_response.status_code = 500
    http_error = httpx.HTTPStatusError(
        'Server Error',
        request=MagicMock(spec=httpx.Request),
        response=mock_response
    )
    mock_response.raise_for_status.side_effect = http_error
    mock_client.get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        result = await flow_service.flow_type_selection(phone_number)


@pytest.mark.asyncio
async def test_flow_type_selection_retry_success(flow_service_fixture, config_fixture):

    flow_service, mock_client, mock_response = flow_service_fixture
    mock_request = AsyncMock(spec=httpx.Request)
    mock_client.get.side_effect = [
        httpx.TimeoutException('Request timed out'),
        httpx.HTTPStatusError(
            'Server error', request=mock_request, response=httpx.Response(500)),
        httpx.Response(200, content=b'{"flow_type": "repeater"}')
    ]

    result = await flow_service.flow_type_selection('79123456789')
    assert result == {
        'flow_type': 'repeater',
        'available_products': REPEATER_PRODUCTS
    }

    assert mock_client.get.call_count == config_fixture.data_service.retries.max_attempts + 1
