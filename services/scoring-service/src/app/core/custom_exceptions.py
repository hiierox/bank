class UserNotFoundError(Exception):
    """
    Исключение в случае, если пользователь не найден
    """
class LoanAlreadyExistsError(Exception):
    """
    Исключение в случае, если кредит уже записан в историю
    """
