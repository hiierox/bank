from datetime import date

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.config import DBSettings
from app.database.database import Base, get_async_session
from app.database.models import Loan, User
from app.dependencies import get_user_data_service
from app.logic.data_service import UserDataService
from app.service import app

MOCK_PHONE = '79123456789'
MOCK_USER_PROFILE_DATA = {
    'age': 30, 'monthly_income': 50000,
    'employment_type': 'full_time', 'has_property': True
}

MOCK_LOAN_ENTRY_DATA = {
    'loan_id': 'loan_20250115_001', 'product_name': 'LoyaltyLoan',
    'amount': 50000, 'issue_date': date(2025, 1, 15),
    'term_days': 90, 'status': 'open', 'close_date': None
}

@pytest.fixture
async def db_init():

    settings = DBSettings()
    engine = create_async_engine(url=settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def db_session(db_init):
    async_session = async_sessionmaker(
        db_init, expire_on_commit=False, class_=AsyncSession
    )

    async with async_session() as session:
        yield session


@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_async_session] = lambda: db_session
    app.dependency_overrides[get_user_data_service] = lambda: UserDataService(
        db_session)
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url='http://test'
    ) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_user_not_found(client, db_session):
    response = await client.get('/user-data?phone=71231231231')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_user_data_success(client, db_session):
    test_user = User(phone=MOCK_PHONE, **MOCK_USER_PROFILE_DATA)
    test_loan = Loan(user_phone=MOCK_PHONE, **MOCK_LOAN_ENTRY_DATA)
    db_session.add_all([test_user, test_loan])
    await db_session.commit()

    response = await client.get(f'/user-data?phone={MOCK_PHONE}')

    assert response.status_code == 200
    response_data = response.json()
    assert response_data['phone'] == MOCK_PHONE
    assert response_data['profile']['age'] == 30
    assert len(response_data['history']) == 1
    assert response_data['history'][0]['loan_id'] == MOCK_LOAN_ENTRY_DATA['loan_id']


@pytest.mark.asyncio
async def test_put_user_data_create_user_returns_201(client, db_session):
    request_data = {
        'phone': MOCK_PHONE,
        'profile': MOCK_USER_PROFILE_DATA,
        'loan_entry': None
    }
    response = await client.put('/user-data', json=request_data)

    assert response.status_code == 201

    db_user = await db_session.get(User, MOCK_PHONE)
    assert db_user is not None
    assert db_user.age == 30


@pytest.mark.asyncio
async def test_put_user_data_update_user_returns_200(client, db_session):
    db_session.add(User(phone=MOCK_PHONE, **MOCK_USER_PROFILE_DATA))
    await db_session.commit()

    request_data = {
        'phone': MOCK_PHONE,
        'profile': {
            'age': 31, 'monthly_income': 60000,
            'employment_type': 'freelance', 'has_property': False},
        'loan_entry': None
    }
    response = await client.put('/user-data', json=request_data)

    assert response.status_code == 200

    await db_session.refresh(await db_session.get(User, MOCK_PHONE))
    db_user = await db_session.get(User, MOCK_PHONE)
    assert db_user.age == 31
    assert db_user.employment_type == 'freelance'


@pytest.mark.asyncio
async def test_put_user_data_add_loan_to_existing_user(client, db_session):
    db_session.add(User(phone=MOCK_PHONE, **MOCK_USER_PROFILE_DATA))
    await db_session.commit()

    request_data = {
        'phone': MOCK_PHONE,
        'profile': None,
        'loan_entry': {
            **MOCK_LOAN_ENTRY_DATA,
            'issue_date': MOCK_LOAN_ENTRY_DATA['issue_date'].isoformat() # type: ignore
        }
    }
    response = await client.put('/user-data', json=request_data)

    assert response.status_code == 200
    db_loan = await db_session.get(Loan, MOCK_LOAN_ENTRY_DATA['loan_id'])
    assert db_loan is not None
    assert db_loan.user_phone == MOCK_PHONE


@pytest.mark.asyncio
async def test_put_user_data_update_loan(client, db_session):
    test_user = User(phone=MOCK_PHONE, **MOCK_USER_PROFILE_DATA)
    test_loan = Loan(user_phone=MOCK_PHONE, **MOCK_LOAN_ENTRY_DATA)
    db_session.add_all([test_user, test_loan])
    await db_session.commit()

    request_data = {
        'phone': MOCK_PHONE,
        'profile': None,
        'loan_entry': {
            'loan_id': MOCK_LOAN_ENTRY_DATA['loan_id'],
            'status': 'closed', 'close_date': '2025-04-15'
        }
    }
    response = await client.put('/user-data', json=request_data)

    assert response.status_code == 200
    db_loan = await db_session.get(Loan, MOCK_LOAN_ENTRY_DATA['loan_id'])
    assert db_loan.status == 'closed'
    assert db_loan.close_date == date(2025, 4, 15)


@pytest.mark.asyncio
async def test_put_user_data_loan_already_exists(client, db_session):
    test_user = User(phone=MOCK_PHONE, **MOCK_USER_PROFILE_DATA)
    test_loan = Loan(user_phone=MOCK_PHONE, **MOCK_LOAN_ENTRY_DATA)
    db_session.add_all([test_user, test_loan])
    await db_session.commit()

    request_data = {
        'phone': MOCK_PHONE, 'profile': None,
        'loan_entry': {
            **MOCK_LOAN_ENTRY_DATA,
            'issue_date': MOCK_LOAN_ENTRY_DATA['issue_date'].isoformat() # type: ignore
        }
    }
    response = await client.put('/user-data', json=request_data)

    assert response.status_code == 422
    assert response.json() == {'detail': 'Loan already exists'}


@pytest.mark.asyncio
async def test_put_user_data_user_not_found(client: AsyncClient):
    request_data = {
        'phone': MOCK_PHONE, 'profile': None,
        'loan_entry': {
            **MOCK_LOAN_ENTRY_DATA,
            'issue_date': MOCK_LOAN_ENTRY_DATA['issue_date'].isoformat() # type: ignore
        }
    }
    response = await client.put('/user-data', json=request_data)

    assert response.status_code == 404
    assert response.json() == {'detail': 'User not found'}
