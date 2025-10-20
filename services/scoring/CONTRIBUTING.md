# Установка и запуск сервиса

```bash
poetry install --no-root
export PYTHONPATH=$pwd:src
poetry run uvicorn app.service:app 
```

Документация доступна по адресу
`http://127.0.0.1:8000/docs`


# Запуск тестов

```bash
poetry run pytest
```
