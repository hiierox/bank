# Установка и запуск сервиса

```bash
poetry install --no-root
poetry run uvicorn src.app.service:app 
```

Документация доступна по адресу
`http://127.0.0.1:8000/docs`


# Запуск тестов
Временное решение

```bash
eval $(poetry env activate)
export PYTHONPATH=$pwd:src
pytest
```
