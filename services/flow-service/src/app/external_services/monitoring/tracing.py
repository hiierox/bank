import logging
import os

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.propagate import get_global_textmap
from opentelemetry.propagators.textmap import TextMapPropagator
from opentelemetry.sdk.resources import SERVICE_NAME as OTLP_SERVICE_NAME
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

logger = logging.getLogger(__name__)

SERVICE_NAME = 'flow-selection-service-kbatrakov'
OTLP_ENDPOINT = os.environ.get(
    'OTEL_EXPORTER_OTLP_ENDPOINT',
    'http://infra-jaeger-collector.infra.svc.cluster.local:4318'
)
OTLP_URL = f'{OTLP_ENDPOINT}/v1/traces'


def setup_tracing(app: FastAPI) -> None:
    """Настраивает OpenTelemetry Tracer Provider и экспортеры."""

    resource = Resource(
        attributes={
            OTLP_SERVICE_NAME: SERVICE_NAME,
            'service.version': os.environ.get('SERVICE_VERSION', '1.0.0'),
        }
    )

    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    span_exporter = OTLPSpanExporter(endpoint=OTLP_URL)

    span_processor = BatchSpanProcessor(span_exporter)
    provider.add_span_processor(span_processor)

    FastAPIInstrumentor.instrument_app(app)
    HTTPXClientInstrumentor().instrument()

    logger.info(
        f'OpenTelemetry трейсинг настроен: endpoint: {OTLP_URL},service: {SERVICE_NAME}'
    )


def get_tracer() ->  trace.Tracer:
    """Получить tracer для ручного создания spans."""
    return trace.get_tracer(__name__)

def get_kafka_propagator() -> TextMapPropagator:
    """Получить глобальный TextMapPropagator для работы c заголовками Kafka."""
    return get_global_textmap()
