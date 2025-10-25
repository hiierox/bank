# Установка и запуск сервиса

```bash
poetry install --no-root
```
Запуск из корня проекта - services/scoring 
`sh run.sh`

Документация доступна по адресу
`http://127.0.0.1:8001/docs`

Тестовые данные для api/scoring/pionner:
```{
  "user_data": {
    "phone": "71112223330",
    "age": 25,
    "monthly_income": 44440,
    "employment_type": "full_time",
    "has_property": true
  },
  "products": [
    {
      "name": "QuickMoney",
      "max_amount": 10000,
      "term_days": 10,
      "interest_rate_daily": 5
    }
  ]
}

Для repeater:
loan_id сделал по времени без секунд чтобы можно было наглядно увидеть ошибку LoanAlreadyExistsError. То есть два раза в течение минуты попытаться отправить запрос на один номер
{
  "phone": "71112223330",
  "products": [
    {
      "name": "PrimeCredit",
      "max_amount": 1000,
      "term_days": 10,
      "interest_rate_daily": 10
    }
  ]
}
```
# Запуск тестов

```bash
poetry run pytest
```
