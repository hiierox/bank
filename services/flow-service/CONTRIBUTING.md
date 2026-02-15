# Локальная разработка

- `poetry install --no-root`
- В корне сервиса создать `.env`: `DATA_SERVICE_BASE_URL`, `DATA_SERVICE_TIMEOUT`, `DATA_SERVICE_DELAY`, `DATA_SERVICE_MAX_ATTEMPTS`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_TTL` (примеры в docker-compose).
- Остальной стек: из корня проекта `docker compose up -d` **без** flow-service.
- Запуск: из `services/flow-service` выполнить `./run.sh` (или `poetry run uvicorn ...`).
- Тесты: `poetry run pytest`
- API docs: http://127.0.0.1:8000/docs
