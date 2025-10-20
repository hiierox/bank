from datetime import datetime
from zoneinfo import ZoneInfo

from app.api.scoring.schemas import ClientProfile, CreditHistoryItem, Product, UserData

from .client_records_tmp import (
    PERFECT_REPEATER_PROFILE,
    REJECTED_REPEATER_PROFILE,
    RISKY_REPEATER_PROFILE,
)

CLIENT_PROFILE_DB: dict[str, ClientProfile] = {
    PERFECT_REPEATER_PROFILE.user_data.phone: PERFECT_REPEATER_PROFILE,
    RISKY_REPEATER_PROFILE.user_data.phone: RISKY_REPEATER_PROFILE,
    REJECTED_REPEATER_PROFILE.user_data.phone: REJECTED_REPEATER_PROFILE
}


class ClientProfileRepository:

    async def save_user_profile(self, user_data: UserData) -> None:
        """
        Сохранение профиля пользователя в базу данных
        """
        CLIENT_PROFILE_DB[user_data.phone] = ClientProfile(user_data=user_data)

    async def save_user_credit_history(self, phone: str,
                                       product: Product) -> None:
        """
        Сохранение выданного кредита в профиль пользователя
        """
        credit_history = CreditHistoryItem(product_name=product.name,
                                           amount=product.max_amount,
                                           issue_date=datetime.now(
                                               tz=ZoneInfo('UTC')).date(),
                                           term_days=product.term_days,
                                           status='open'
                                           )
        CLIENT_PROFILE_DB[phone].credit_history.append(credit_history)

    async def get_user_profile(self, phone: str) -> ClientProfile | None:
        return CLIENT_PROFILE_DB.get(phone)
