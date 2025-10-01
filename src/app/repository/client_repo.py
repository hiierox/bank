phone_numbers_db = set()


class ClientRepository:
    """
    Репозиторий номеров телефона клиентов
    """

    async def is_number_known(self, incoming_phone_number: str) -> bool:
        """
        Проверяет есть ли входящий номер в базе данных
        """
        return incoming_phone_number in phone_numbers_db

    async def add_number(self, phone_number: str) -> None:
        """
        Добавляет номер телефона в базу данных
        """
        phone_numbers_db.add(phone_number)
