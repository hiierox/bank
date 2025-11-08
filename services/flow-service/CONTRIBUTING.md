# Установка и запуск сервиса


### Для локального запуска
```bash
poetry install --no-root
```
Создать `.env` в корне сервиса
```
DATA_SERVICE_DELAY=1
DATA_SERVICE_BASE_URL=http://localhost:8002
DATA_SERVICE_TIMEOUT=5
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_TTL=60
```
`docker-compose up -d` без flow-serivce

Запуск этого сервиса из корня проекта - services/flow_service 
`sh run.sh`

Документация доступна по адресу
`http://127.0.0.1:8000/docs`

# Запуск тестов

```bash
poetry run pytest
```
В базе `79123456789` уже есть для сценария repeater
