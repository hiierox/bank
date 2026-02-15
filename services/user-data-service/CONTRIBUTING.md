# Локальная разработка

- `poetry install --no-root`
- В корне сервиса создать `.env`: `DATABASE_URL` (PostgreSQL), `KAFKA_BOOTSTRAP_SERVERS`, `KAFKA_TOPIC`, `KAFKA_GROUP_ID` (значения — в docker-compose или основном README).
- Остальной стек: из корня проекта `docker compose up -d` **без** data-service. Перед первым запуском: `poetry run alembic upgrade head`.
- Запуск: из `services/user-data-service` выполнить `./run.sh`.
- Тесты: `poetry run pytest`
- API docs: http://127.0.0.1:8002/docs
