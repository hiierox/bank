from collections.abc import Sequence
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.custom_exceptions import LoanNotFoundError

from .models import Loan, Product, User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_profile(self, phone: str) -> User | None:
        """
        Возвращает профиль пользователя
        """
        request = select(User).where(
            User.phone == phone).options(selectinload(User.loans))
        result = await self.session.execute(request)
        return result.scalars().first()

    async def update_or_create_user_profile(self, user_data: User) -> bool:
        """
        Создает или обновляет профиль пользователя.
        Возвращает True, если профиль создан, False, если обновлен
        """
        user_exist = await self.session.get(User, user_data.phone)

        if user_exist:
            user_exist.age = user_data.age
            user_exist.monthly_income = user_data.monthly_income
            user_exist.employment_type = user_data.employment_type
            user_exist.has_property = user_data.has_property
            return False
        else:  # noqa: RET505
            self.session.add(user_data)
            return True


class LoanRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def is_loan_entry_in_db(self, loan_id: str) -> bool:
        """
        Проверяет есть ли кредит в истории
        """
        existing_loan = await self.session.get(Loan, loan_id)
        return existing_loan is not None

    async def add_new_loan_entry(self, loan_entry: Loan) -> None:
        """
        Добавляет новую запись в историю кредитов
        """
        self.session.add(loan_entry)

    async def update_loan_entry(
        self,
        loan_id: str,
        status: str,
        close_date: date | None
    ) -> None:
        """
        Обновляет запись o кредите
        """
        loan = await self.session.get(Loan, loan_id)

        if not loan:
            raise LoanNotFoundError

        loan.status = status
        loan.close_date = close_date


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_products_list(self, flow_type: str | None) -> Sequence[Product]:
        """Возвращает список продуктов в зависимости от flow_type.
        Если flow_type == None, возвращает все продукты
        """
        request = select(Product)
        if flow_type:
            request = request.where(Product.flow_type == flow_type)
        result = await self.session.scalars(request)
        return result.all()
