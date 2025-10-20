from unittest.mock import AsyncMock
from fastapi import HTTPException
import pytest
from tests.unit.mock_scoring_data import (
    MOCK_PRODUCT_ADVANTAGE,
    MOCK_PRODUCT_LOYALTY,
    MOCK_PRODUCT_PRIMECREDIT,
    MOCK_PRODUCTS_PIONEER,
    MOCK_PRODUCTS_REPEATER,
    MOCK_TEST_PROFILE_BAD_BUT_GOOD_HISTORY,
    MOCK_TEST_PROFILE_FULL_POINTS,
    MOCK_TEST_PROFILE_LOW_AGE,
    MOCK_TEST_PROFILE_LOW_POINTS,
    MOCK_TEST_PROFILE_LOYALTY,
    MOCK_TEST_PROFILE_OPEN_CREDIT,
    MOCK_TEST_PROFILE_SUCCESS,
    MOCK_USER_DATA_FAIL,
    MOCK_USER_DATA_REJECT,
    MOCK_USER_DATA_SUCCESS,
    TWO_PRODUCTS,
    FULL_PACK_PRODUCTS
)

from app.external_service.get_credit_status_service import get_credit_status
from app.logic.scoring import UserScoring
from app.repository.client_repo import ClientProfileRepository
from app.core.custom_exceptions import UserNotFoundError


@pytest.fixture
def user_scoring_fixture():
    mock_client_repo = AsyncMock(spec=ClientProfileRepository)
    scoring_service = UserScoring(mock_client_repo)
    return mock_client_repo, scoring_service


@pytest.fixture
def get_credit_status_fixture():
    get_credit_status = AsyncMock()
    return get_credit_status


@pytest.mark.asyncio
async def test_user_scoring_pioneer_accepted_quickmoney(user_scoring_fixture):
    client_repo, scoring_service = user_scoring_fixture

    result = await scoring_service.user_scoring_pioneer(
        user_data=MOCK_USER_DATA_SUCCESS,
        products=MOCK_PRODUCTS_PIONEER
    )

    assert result['decision'] == 'accepted'
    assert result['product'].model_dump(
    ) == MOCK_PRODUCTS_PIONEER[1].model_dump()
    client_repo.save_user_profile.assert_called_once()


@pytest.mark.asyncio
async def test_user_scoring_pioneer_rejected_low_score(user_scoring_fixture):
    client_repo, scoring_service = user_scoring_fixture

    result = await scoring_service.user_scoring_pioneer(user_data=MOCK_USER_DATA_REJECT,
                                                        products=MOCK_PRODUCTS_PIONEER)

    assert result['decision'] == 'rejected'
    assert result['product'] is None
    client_repo.save_user_profile.assert_not_called()


@pytest.mark.asyncio
async def test_user_scoring_pioneer_rejected_fail(user_scoring_fixture):
    client_repo, scoring_service = user_scoring_fixture

    result = await scoring_service.user_scoring_pioneer(user_data=MOCK_USER_DATA_FAIL,
                                                        products=MOCK_PRODUCTS_PIONEER)

    assert result['decision'] == 'rejected'
    assert result['product'] is None
    client_repo.save_user_profile.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize('user_profile, user_product, products',
                         [
                             pytest.param(
                                 MOCK_TEST_PROFILE_LOYALTY,
                                 MOCK_PRODUCT_LOYALTY,
                                 FULL_PACK_PRODUCTS,
                                 id='return value: Loyalty'
                             ),
                             pytest.param(
                                 MOCK_TEST_PROFILE_SUCCESS,
                                 MOCK_PRODUCT_ADVANTAGE,
                                 FULL_PACK_PRODUCTS,
                                 id='return value: Advantage'
                             ),
                             pytest.param(
                                 MOCK_TEST_PROFILE_BAD_BUT_GOOD_HISTORY,
                                 MOCK_PRODUCT_PRIMECREDIT,
                                 FULL_PACK_PRODUCTS,
                                 id='return value: Prime'
                             ),
                             pytest.param(
                                 MOCK_TEST_PROFILE_FULL_POINTS,
                                 MOCK_PRODUCT_ADVANTAGE,
                                 TWO_PRODUCTS,
                                 id='return value: Advantage'
                             )
                         ]
                         )
async def test_user_scoring_repeater_accepted(user_scoring_fixture,
                                              get_credit_status_fixture,
                                              user_profile,
                                              user_product,
                                              products):
    phone = '79123456789'
    client_repo, scoring_service = user_scoring_fixture
    client_repo.get_user_profile.return_value = user_profile
    get_credit_status_fixture.return_value = 'closed'

    result = await scoring_service.user_scoring_repeater(phone, products)

    assert result['decision'] == 'accepted'
    assert result['product'] == user_product[0]
    client_repo.save_user_credit_history.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize('user_profile', [
                         (MOCK_TEST_PROFILE_LOW_AGE),
                         (MOCK_TEST_PROFILE_LOW_POINTS),
                         (MOCK_TEST_PROFILE_OPEN_CREDIT),
                         ],
                         ids=('low_age',
                              'low_points',
                              'last_credit_open_longer_6_months')

                         )
async def test_user_scoring_repeater_rejected(user_scoring_fixture,
                                              get_credit_status_fixture,
                                              user_profile,
                                              ):
    phone = '79123456789'
    products = FULL_PACK_PRODUCTS
    client_repo, scoring_service = user_scoring_fixture
    client_repo.get_user_profile.return_value = user_profile
    get_credit_status_fixture.return_value = 'open'

    result = await scoring_service.user_scoring_repeater(phone, products)

    assert result['decision'] == 'rejected'
    assert result['product'] is None
    client_repo.save_user_credit_history.assert_not_called()


@pytest.mark.asyncio
async def test_user_scoring_repeater_not_found(user_scoring_fixture):
    phone = '79123456789'
    products = FULL_PACK_PRODUCTS
    client_repo, scroing_service = user_scoring_fixture
    client_repo.get_user_profile.return_value = None

    with pytest.raises(UserNotFoundError) as e:
        await scroing_service.user_scoring_repeater(phone, products)

    client_repo.save_user_credit_history.assert_not_called()
