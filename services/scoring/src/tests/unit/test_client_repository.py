import pytest

from app.api.scoring.schemas import UserData
from app.repository.client_repo import ClientProfileRepository, user_data_db

MOCK_USER_DATA = UserData(
    phone='79123456789',
    age=25,
    monthly_income=45000,
    employment_type='full_time',
    has_property=True
)


@pytest.fixture
def clear_db():
    user_data_db.clear()
    yield
    user_data_db.clear()


@pytest.mark.asyncio
async def test_save_user_profile_success(clear_db):
    repo = ClientProfileRepository()

    await repo.save_user_profile(MOCK_USER_DATA)

    assert len(user_data_db) == 1
    assert MOCK_USER_DATA.model_dump() in user_data_db
