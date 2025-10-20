# Установка и запуск сервиса

```bash
poetry install --no-root
export PYTHONPATH=$pwd:src
poetry run uvicorn app.service:app 
```

Документация доступна по адресу
`http://127.0.0.1:8000/docs`
Тестовые данные для repeater 
Клиенты с доступом:
    - ко всем кредитам - 79123456789
    - к LoyaltyLoan - 71234567890
    - без доступа - 79876543210

# Запуск тестов

```bash
poetry run pytest
```
