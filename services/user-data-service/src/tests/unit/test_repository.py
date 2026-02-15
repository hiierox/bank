from datetime import date

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.custom_exceptions import LoanNotFoundError
from app.database.database import Base
from app.database.models import Loan, User
from app.database.repository import LoanRepository, UserRepository


@pytest.fixture
async def session_maker():
    """
    Создает in-memory SQLite базу для каждого теста
    Возвращает фабрику сессий
    """
    engine = create_async_engine('sqlite+aiosqlite:///:memory:')

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(engine, expire_on_commit=False)

    yield session_maker

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.mark.asyncio
async def test_user_repo_get_user_profile(session_maker):
    """Получение пользователя по телефону"""
    async with session_maker() as session:
        test_user = User(
            phone='71234567890', age=30, monthly_income=50000,
            employment_type='full_time', has_property=True
        )
        session.add(test_user)
        await session.commit()

        repo = UserRepository(session)
        found_user = await repo.get_user_profile('71234567890')

        assert found_user is not None
        assert found_user.phone == '71234567890'
        assert found_user.age == 30


@pytest.mark.asyncio
async def test_user_repo_get_user_profile_not_found(session_maker):
    """get_user_profile возвращает None, если пользователь не найден."""
    async with session_maker() as session:
        repo = UserRepository(session)

        found_user = await repo.get_user_profile('phone')

        assert found_user is None


@pytest.mark.asyncio
async def test_user_repo_create_or_update(session_maker):
    """Создание и обновление пользователя."""
    async with session_maker() as session:
        repo = UserRepository(session)

        new_user_data = User(
            phone='79998887766', age=25, monthly_income=60000,
            employment_type='freelance', has_property=False
        )
        is_created = await repo.update_or_create_user_profile(new_user_data)
        await session.commit()

        assert is_created is True
        created_user = await session.get(User, '79998887766')
        assert created_user.age == 25

        updated_user_data = User(
            phone='79998887766', age=26, monthly_income=70000,
            employment_type='full_time', has_property=True
        )
        is_created = await repo.update_or_create_user_profile(updated_user_data)
        await session.commit()

        assert is_created is False
        updated_user = await session.get(User, '79998887766')
        assert updated_user.age == 26
        assert updated_user.has_property is True


@pytest.mark.asyncio
async def test_loan_repo_add_and_exists(session_maker):
    """Добавление и проверка существования кредита в бд"""
    async with session_maker() as session:
        user = User(
            phone='71112223344', age=30, monthly_income=1,
            employment_type='freelance', has_property=False
        )
        session.add(user)
        await session.commit()

        repo = LoanRepository(session)

        assert await repo.is_loan_entry_in_db('loan123') == False

        new_loan = Loan(
            loan_id='loan123', user_phone='71112223344', product_name='product',
            amount=1000, issue_date=date(2025, 1, 1), term_days=1, status='open'
        )
        await repo.add_new_loan_entry(new_loan)
        await session.commit()

        assert await repo.is_loan_entry_in_db('loan123') == True


@pytest.mark.asyncio
@pytest.mark.parametrize('status, close_date', [
    ('closed', date(2025, 2, 1)),
    ('fake_status', None),
    ('open', None),
])
async def test_loan_repo_update_scenarios(session_maker, status, close_date):
    """Ообновление кредита c разными статусами и датами"""
    async with session_maker() as session:
        user = User(
            phone='71112223344', age=30, monthly_income=1,
            employment_type='ft', has_property=False
        )
        loan = Loan(
            loan_id='loan123', user_phone='71112223344', product_name='p',
                    amount=1, issue_date=date(2025, 1, 1), term_days=1, status='open'
        )
        session.add_all([user, loan])
        await session.commit()

        repo = LoanRepository(session)

        await repo.update_loan_entry(
            loan_id='loan123', status=status, close_date=close_date
        )
        await session.commit()

        updated_loan = await session.get(Loan, 'loan123')
        assert updated_loan is not None
        assert updated_loan.status == status
        assert updated_loan.close_date == close_date


@pytest.mark.asyncio
async def test_loan_repo_update_not_found_raises_error(session_maker):
    """Обновление несуществующего кредита вызывает LoanNotFoundError"""
    async with session_maker() as session:
        repo = LoanRepository(session)
        with pytest.raises(LoanNotFoundError):
            await repo.update_loan_entry(
                loan_id='loan123123', status='closed', close_date=None
            )


@pytest.mark.asyncio
@pytest.mark.parametrize('loan_id, expected', [
    ('loan123', True),
    ('loan_non_exist', False),
])
async def test_loan_repo_is_loan_entry_in_db(session_maker, loan_id, expected):
    """проверка существования кредита"""
    async with session_maker() as session:
        user = User(
            phone='71112223344', age=30, monthly_income=1,
            employment_type='ft', has_property=False
        )
        loan = Loan(
            loan_id='loan123', user_phone='71112223344', product_name='p',
            amount=1000, issue_date=date(2025, 1, 1), term_days=1, status='open'
        )
        session.add_all([user, loan])
        await session.commit()

        repo = LoanRepository(session)

        result = await repo.is_loan_entry_in_db(loan_id)
        assert result is expected
