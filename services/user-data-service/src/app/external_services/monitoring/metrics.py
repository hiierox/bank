from prometheus_client import Counter, Gauge, Histogram

SERVICE_NAME = 'user-data-service-kbatrakov'

http_requests_total = Counter(
    'http_requests_total',
    'Общее количество HTTP запросов',
    ['method', 'endpoint', 'status', 'service']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'Время обработки HTTP запросов в секундах',
    ['method', 'endpoint', 'service'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0]
)

database_latency_seconds = Histogram(
    'database_latency_seconds',
    'Время выполнения операций c БД',
    ['service', 'operation'],
    buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5]
)

user_profile_creations_total = Counter(
    'user_profile_creations_total',
    'Количество новых созданных профилей пользователей',
    ['service']
)

user_profile_updates_total = Counter(
    'user_profile_updates_total',
    'Количество обновлений существующих профилей пользователей',
    ['service']
)

loan_history_additions_total = Counter(
    'loan_history_additions_total',
    'Количество добавленных записей o кредитах',
    ['service', 'product_name']
)

loan_history_updates_total = Counter(
    'loan_history_updates_total',
    'Количество обновлений статуса кредитов',
    ['service', 'status']
)

app_info = Gauge(
    'app_info',
    'Информация o приложении',
    ['version', 'service']
)

app_health_status = Gauge(
    'app_health_status',
    'Статус здоровья приложения (1 = healthy, 0 = unhealthy)'
)

app_ready_status = Gauge(
    'app_ready_status',
    'Статус готовности приложения (1 = ready, 0 = not ready)'
)

external_service_calls_total = Counter(
    'external_service_calls_total',
    'Количество вызовов внешних сервисов',
    ['service_name', 'method', 'endpoint', 'status']
)


def init_service_metrics(
        service_name: str = SERVICE_NAME, version: str = '1.0.0'
) -> None:
    """Инициализация метрик при запуске сервиса."""
    app_info.labels(version=version, service=service_name).set(1)
    app_health_status.set(1)
    app_ready_status.set(1)


def shutdown_service_metrics() -> None:
    """Обновление метрик при остановке сервиса."""
    app_health_status.set(0)
    app_ready_status.set(0)
