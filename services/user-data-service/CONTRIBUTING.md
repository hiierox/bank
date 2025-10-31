# Установка и запуск сервиса

```bash
poetry install --no-root
```
Создать .env в services/user-data-service и добавить `DATABASE_URL=postgresql+asyncpg://shift_user:shift_password@localhost:5432/data_service`

Запустить `docker-compose up -d` (все переменные для БД прямо там указал пока)
Запуск сервиса из корня проекта - services/user-data-service 
`sh run.sh`


Документация доступна по адресу
`http://127.0.0.1:8002/docs`

Тестовые данные автоматически генерируются подходящие.
Для случаев, когда нужно отправить отдельно либо profile, либо loan_entry нужно  
полностью убрать из запроса соответствующий ключ, а не присваивать none, например, без loan_entry:  
{  
  "phone": "76787857177",  
    "profile": {
    "age": 120,  
    "monthly_income": 1,  
    "employment_type": "full_time",  
    "has_property": true  
  }  
  Swagger UI иначе ругается почему-то. В тестах все ок

# Запуск тестов

```bash
poetry run pytest
```
