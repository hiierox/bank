from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import settings
from app.database.database import get_async_session
from app.external_services.kafka_consumer import KafkaConsumerService

router = APIRouter()


@router.get('/up', status_code=200)
async def liveness_probe() -> dict[str, str]:
    """Liveness probe."""
    return {'status': 'ok'}


@router.get('/ready', status_code=200)
async def readiness_probe(
    session: AsyncSession = Depends(get_async_session),
) -> dict[str, str]:
    """
    Readiness probe: проверяет подключение к БД и Kafka.
    """
    try:
        await session.execute(text('SELECT 1'))
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f'Database connection failed: {e}'
        ) from e

    consumer = None
    try:
        consumer = KafkaConsumerService(config=settings)
        await consumer.start()
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f'Kafka connection failed: {e}'
        ) from e
    finally:
        if consumer:
            await consumer.stop()

    return {'status': 'ready'}
