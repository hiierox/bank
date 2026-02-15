# Frontend — демо скоринга

Пошаговая демонстрация: телефон → определение флоу (pioneer/repeater) → ввод данных и выбор кредита → отправка в скоринг → результат. Справа — отладочная панель (доступные кредиты и ответ скоринга).

## Запуск через Docker (рекомендуется)

Из корня проекта:

```bash
docker compose up --build
```

Фронт будет доступен на **http://localhost:3000**. Запросы к API идут через тот же origin (прокси в nginx), поэтому CORS не возникает.

## Локальный запуск (dev)

1. Поднять бэкенд: `docker compose up` (без frontend можно отключить: `docker compose up flow-service scoring-service data-service ...` или поднять всё).
2. В каталоге `frontend`: `npm install` (или `bun install`), затем `npm run dev` (или `bun run dev`).
3. Открыть http://localhost:5173 — запросы к `/api/flow` и `/api/scoring` проксируются на localhost:8000 и 8001 (см. `vite.config.ts`).

## Переменные окружения (сборка / dev)

- `VITE_FLOW_URL` — базовый путь к flow API (по умолчанию `/api/flow` при прокси).
- `VITE_SCORING_URL` — базовый путь к scoring API (по умолчанию `/api/scoring`).

В Docker сборке используются `/api/flow` и `/api/scoring`; при локальном `npm run dev` те же значения и прокси в Vite.
