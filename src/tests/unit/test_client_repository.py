import pytest
from app.repository import client_repo


@pytest.fixture
def clear_db():
    client_repo.phone_numbers_db.clear()
    yield 
    client_repo.phone_numbers_db.clear()


@pytest.mark.asyncio
async def test_is_number_exist(clear_db):
    repo = client_repo.ClientRepository()
    phone_number = '79123456789'
    await repo.add_number(phone_number)

    result = await repo.is_number_known(phone_number)

    assert result == True


@pytest.mark.asyncio
async def test_is_number_not_exist(clear_db):
    repo = client_repo.ClientRepository()
    phone_number = '79123456789'

    result = await repo.is_number_known(phone_number)

    assert result == False


@pytest.mark.asyncio
async def test_add_number(clear_db):
    repo = client_repo.ClientRepository()
    phone_number = '79123456789'
    
    await repo.add_number(phone_number)

    assert await repo.is_number_known(phone_number) == True