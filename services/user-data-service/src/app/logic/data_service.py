from app.api.user_data.schemas import (
    GetUserProfileResponse,
    LoanEntryItem,
    LoanEntryUpdate,
    PutUserProfileRequest,
)
from app.core.custom_exceptions import LoanAlreadyExistError, UserNotFoundError
from app.repository.client_repo import ClientRepository


class UserDataService:
    def __init__(self, client_repo: ClientRepository) -> None:
        self.client_repo = client_repo

    async def get_user_profile(self, phone: str) -> GetUserProfileResponse:
        user_profile = await self.client_repo.get_user_profile(phone)
        if user_profile:
            return GetUserProfileResponse(
                phone=phone,
                profile=user_profile['profile'],
                history=user_profile['history']
            )
        raise UserNotFoundError('User not found')

    async def put_user_data(self, phone: str, request: PutUserProfileRequest) -> bool:
        """
        Обрабатывает PUT запрос.
        Возвращает True, если пользователь создан, False, если обновлён.
        """
        is_new_user = False
        if request.profile:
            is_new_user = await self.client_repo.update_or_create_user_profile(
                phone,
                request.profile
            )

        user_exist = await self.client_repo.get_user_profile(phone)
        if not user_exist:
            raise UserNotFoundError('User not found')

        if request.loan_entry:
            if isinstance(request.loan_entry, LoanEntryItem):
                is_loan_in_db = await self.client_repo.is_loan_entry_in_db(
                    phone,
                    request.loan_entry.loan_id
                )
                if not is_loan_in_db:
                    await self.client_repo.add_new_loan_entry(phone, request.loan_entry)
                else:
                    raise LoanAlreadyExistError
            elif isinstance(request.loan_entry, LoanEntryUpdate):
                await self.client_repo.update_loan_entry(phone, request.loan_entry)
        return is_new_user
