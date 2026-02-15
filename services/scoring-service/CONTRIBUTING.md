# Локальная разработка

- `poetry install --no-root`
- В корне сервиса создать `.env`: `DATA_SERVICE_BASE_URL`, `ANTIFRAUD_SERVICE_BASE_URL`, таймауты, `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`, `KAFKA_GROUP_ID` (значения — в docker-compose или основном README).
- Остальной стек: из корня проекта `docker compose up -d` **без** scoring-service.
- Запуск: из `services/scoring-service` выполнить `./run.sh`.
- Тесты: `poetry run pytest`
- API docs: http://127.0.0.1:8001/docs

Тестовые тела запросов для pioneer/repeater — в Swagger или в интеграционных тестах.
