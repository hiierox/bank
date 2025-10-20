from app.api.scoring.schemas import CreditHistoryItem


async def get_credit_status(credit: CreditHistoryItem) -> str:
    """
    Функция заглушка, имитирующая работу внешнего сервиса, который
    возвращает информацию o статусе кредита (открыт/закрыт).
    Пока что возвращает имеющийся статус
    """
    return credit.status
