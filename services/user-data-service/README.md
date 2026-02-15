# user-data-service (data-service)

Хранит профили и историю заявок клиентов в PostgreSQL  
Обновление данных — по событиям из Kafka (топик `scoring_results`). Отдаёт профиль по телефону (для flow-service и antifraud-service).

**Функции:** GET по телефону (есть/нет пользователя), приём событий из Kafka — создание/обновление профиля и истории займов. Миграции — Alembic.

**Зависимости:** PostgreSQL, Kafka.  
**Порт:** 8002.  
**Документация API:** `/docs`.

Подробнее по запуску и тестам — `CONTRIBUTING.md`.
