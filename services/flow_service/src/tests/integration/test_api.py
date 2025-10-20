import pytest
from fastapi.testclient import TestClient

from app.repository import client_repo, product_repo
from app.service import app


@pytest.fixture
def client():
    client_repo.phone_numbers_db.clear()
    test_client = TestClient(app)

    yield test_client

    client_repo.phone_numbers_db.clear()


@pytest.mark.asyncio
async def test_case_pioneer_then_repeater(client):
    phone_data = {'phone_number': '79123456789'}

    response = client.post('api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'pioneer'
    assert len(response_data['available_products']) > 0
    assert phone_data['phone_number'] in client_repo.phone_numbers_db
    assert response_data['available_products'] == product_repo.PIONEER_PRODUCTS

    response = client.post('api/products', json=phone_data)

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['flow_type'] == 'repeater'
    assert response_data['available_products'] == product_repo.REPEATER_PRODUCTS



@pytest.mark.asyncio
async def test_wrong_phone_numbers_format(client):
    phones_data = [
                {'phone_number': '79123456789a'},
                {'phone_number': '89123456789'},
                {'phone_number': '790'}
                ]

    for phone_data in phones_data:
        response = client.post('api/products', json=phone_data)

        assert response.status_code == 422
