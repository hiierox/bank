# Установка и запуск сервиса

```bash
poetry install --no-root
```
Запуск из корня проекта - services/flow_service 
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
