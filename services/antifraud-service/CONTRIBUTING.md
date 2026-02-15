# Локальная разработка

- `poetry install --no-root`
- В корне сервиса создать `.env`: `DATA_SERVICE_BASE_URL`, `DATA_SERVICE_TIMEOUT`, `REDIS_HOST`, `REDIS_PORT` (значения — в docker-compose).
- Остальной стек: из корня проекта `docker compose up -d` **без** antifraud-service.
- Запуск: из `services/antifraud-service` — `poetry run uvicorn app.service:app --host 0.0.0.0 --port 8080` (или аналог из Dockerfile).
- Тесты: `poetry run pytest`
- API docs: http://127.0.0.1:8003/docs
