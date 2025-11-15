from aiokafka import AIOKafkaProducer
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import settings
from app.database.database import get_async_session

router = APIRouter()


@router.get('/up', status_code=200)
async def liveness_probe():
    """Liveness probe."""
    return {'status': 'ok'}


@router.get('/ready', status_code=200)
async def readiness_probe(session: AsyncSession = Depends(get_async_session)):
    """
    Readiness probe: проверяет подключение к БД и Kafka.
    """
    try:
        await session.execute(text('SELECT 1'))
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f'Database connection failed: {e}') from e

    producer = None
    try:
        producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        await producer.start()
        await producer.client.fetch_all_metadata()
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f'Kafka connection failed: {e}') from e
    finally:
        if producer:
            await producer.stop()

    return {'status': 'ready'}
