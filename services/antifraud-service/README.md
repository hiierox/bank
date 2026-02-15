# antifraud-service

Проверки антифрода для pioneer (новый клиент) и repeater (повторный): правила по данным заявки, счётчик заявок в Redis, для repeater — запрос профиля в data-service.

**Функции:** эндпоинты `/api/antifraud/pioneer/check` и `/api/antifraud/repeater/check`; при прохождении — инкремент счётчика в Redis.

**Зависимости:** data-service, Redis.  
**Порт:** 8003.  
**Документация API:** `/docs`.

Подробнее по запуску и тестам — `CONTRIBUTING.md`.
