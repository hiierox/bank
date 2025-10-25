from typing import Any

from app.api.user_data.schemas import LoanEntryItem, LoanEntryUpdate, UserProfile
from app.core.custom_exceptions import LoanNotFoundError, UserNotFoundError

USER_PROFILE_DB: dict[str, dict[str, Any]] = {'79123456789':
         {'profile':
          UserProfile(age=25,
                      monthly_income=30000,
                      employment_type='full_time',
                      has_property=True),
          'history': []
          }}


class ClientRepository:
    async def get_user_profile(self, phone: str) -> dict[str, Any] | None:
        return USER_PROFILE_DB.get(phone)

    async def is_loan_entry_in_db(self,
                                  phone: str,
                                  loan_id: str
                                  ) -> bool:
        """
        Проверяет, есть ли loan_id в базе данных.
        Если есть - возвращает True,
        Если нет - возращает False
        """
        if phone not in USER_PROFILE_DB:
            raise UserNotFoundError('User not found')

        for loan_db in USER_PROFILE_DB[phone]['history']:
            if loan_id == loan_db.loan_id:
                return True
        return False

    async def update_or_create_user_profile(self,
                                            phone: str,
                                            user_data: UserProfile,
                                            ) -> bool:
        """
        Создает новый профиль или обновляет существующий.
        """
        if phone not in USER_PROFILE_DB:
            USER_PROFILE_DB[phone] = {'profile': user_data, 'history': []}
            return True

        USER_PROFILE_DB[phone]['profile'] = user_data
        return False

    async def add_new_loan_entry(self, phone: str, loan_entry: LoanEntryItem) -> None:
        """
        Добавляет новую запись кредита.
        """
        if phone not in USER_PROFILE_DB:
            raise UserNotFoundError('User not found')

        USER_PROFILE_DB[phone]['history'].append(loan_entry)

    async def update_loan_entry(self, phone: str, loan_entry: LoanEntryUpdate,) -> None:
        """
        Обновляет запись кредита.
        """
        if phone not in USER_PROFILE_DB:
            raise UserNotFoundError('User not found')

        for i, existing_loan in enumerate(USER_PROFILE_DB[phone]['history']):
            if existing_loan.loan_id == loan_entry.loan_id:
                update_data = loan_entry.model_dump(exclude_unset=True)
                updated_loan = existing_loan.model_copy(update=update_data)
                USER_PROFILE_DB[phone]['history'][i] = updated_loan
                return
        raise LoanNotFoundError
