class UserNotFoundError(Exception):
    """
    Исключение если пользователь не найден
    """


class LoanNotFoundError(Exception):
    """
    Исключение если запись кредита не найдена
    """


class LoanAlreadyExistError(Exception):
    """
    Исключение если запись кредита найдена
    """
