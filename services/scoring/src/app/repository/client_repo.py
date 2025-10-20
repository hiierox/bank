from app.api.scoring.schemas import UserData

user_data_db = []


class ClientProfileRepository:

    async def save_user_profile(self, user_data: UserData) -> None:
        """
        Сохранение профиля пользователя в базу данных
        """
        user_data_db.append(user_data.model_dump())
