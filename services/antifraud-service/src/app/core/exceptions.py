class IntegrationError(Exception):
    """
    Исключение для ошибок, связанных c внешними интеграциями
    """


class DataServiceNotFoundError(Exception):
    """
    Исключение для 404 от data-service.
    Считается ошибкой потока, так как пользователь REPEATER должен существовать.
    """
