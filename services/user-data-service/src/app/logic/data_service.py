from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user_data.schemas import (
    GetUserProfileResponse,
    LoanEntryItem,
    LoanEntryUpdate,
    ProductResponse,
    PutUserProfileRequest,
    UserProfile,
)
from app.core.custom_exceptions import LoanAlreadyExistError, UserNotFoundError
from app.database.models import Loan, User
from app.database.repository import LoanRepository, ProductRepository, UserRepository
from app.external_services.monitoring.metrics import (
    SERVICE_NAME,
    database_latency_seconds,
    loan_history_additions_total,
    loan_history_updates_total,
    user_profile_creations_total,
    user_profile_updates_total,
)


class UserDataService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_user_profile(self, phone: str) -> GetUserProfileResponse:
        """Получает профиль пользователя из базы данных"""

        user_repo = UserRepository(self.session)
        with database_latency_seconds.labels(
            service=SERVICE_NAME, operation='get_user_profile'
        ).time():
            user = await user_repo.get_user_profile(phone)

        if user:
            return GetUserProfileResponse(
                phone=user.phone,
                profile=UserProfile(
                    age=user.age,
                    monthly_income=user.monthly_income,
                    employment_type=user.employment_type,
                    has_property=user.has_property
                ),
                history=[
                    LoanEntryItem.model_validate(loan) for loan in user.loans
                ]
            )
        raise UserNotFoundError('User not found')

    async def put_user_data(self, phone: str, request: PutUserProfileRequest) -> bool:
        """
        Обрабатывает PUT запрос.
        Возвращает True, если пользователь создан, False, если обновлён.
        """
        is_new_user = False
        async with self.session.begin():
            user_repo = UserRepository(self.session)
            loan_repo = LoanRepository(self.session)

            if request.profile:
                db_user = User(
                    phone=phone,
                    age=request.profile.age,
                    monthly_income=request.profile.monthly_income,
                    employment_type=request.profile.employment_type,
                    has_property=request.profile.has_property
                )
                with database_latency_seconds.labels(
                    service=SERVICE_NAME, operation='update_or_create_user_profile'
                ).time():
                    is_new_user = await user_repo.update_or_create_user_profile(db_user)

                if is_new_user:
                    user_profile_creations_total.labels(service=SERVICE_NAME).inc()
                else:
                    user_profile_updates_total.labels(service=SERVICE_NAME).inc()

            with database_latency_seconds.labels(
                service=SERVICE_NAME, operation='get_user_profile'
            ).time():
                user_exist = await user_repo.get_user_profile(phone)

            if not user_exist:
                raise UserNotFoundError('User not found')

            if request.loan_entry:
                if isinstance(request.loan_entry, LoanEntryItem):
                    with database_latency_seconds.labels(
                        service=SERVICE_NAME,
                        operation='is_loan_entry_in_db'
                        ).time():
                        is_loan_in_db = await loan_repo.is_loan_entry_in_db(
                            request.loan_entry.loan_id
                        )
                    if is_loan_in_db:
                        raise LoanAlreadyExistError

                    db_loan = Loan(
                        loan_id=request.loan_entry.loan_id,
                        user_phone=phone,
                        product_name=request.loan_entry.product_name,
                        amount=request.loan_entry.amount,
                        issue_date=request.loan_entry.issue_date,
                        term_days=request.loan_entry.term_days,
                        status=request.loan_entry.status,
                        close_date=request.loan_entry.close_date
                    )
                    with database_latency_seconds.labels(
                        service=SERVICE_NAME, operation='add_new_loan_entry'
                        ).time():
                        await loan_repo.add_new_loan_entry(db_loan)
                    loan_history_additions_total.labels(
                        service=SERVICE_NAME,
                        product_name=request.loan_entry.product_name
                    ).inc()
                elif isinstance(request.loan_entry, LoanEntryUpdate):
                    with database_latency_seconds.labels(
                        service=SERVICE_NAME, operation='update_loan_entry'
                        ).time():
                        await loan_repo.update_loan_entry(
                            loan_id=request.loan_entry.loan_id,
                            status=request.loan_entry.status,
                            close_date=request.loan_entry.close_date
                        )
                    loan_history_updates_total.labels(
                        service=SERVICE_NAME,
                        status=request.loan_entry.status
                    ).inc()
        return is_new_user

    async def get_products_list(
        self, flow_type: str | None
    ) -> list[ProductResponse] | dict[str, str]:
        product_repo = ProductRepository(self.session)
        with database_latency_seconds.labels(
            service=SERVICE_NAME, operation='get_products_list'
            ).time():
            result = await product_repo.get_products_list(flow_type)
        if result:
            return [ProductResponse.model_validate(p) for p in result]
        return {'message': 'Products unavailable'}
