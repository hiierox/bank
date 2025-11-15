from aiokafka import AIOKafkaClient
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.config import settings
from app.database.database import get_async_session

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

    client = None
    try:
        client = AIOKafkaClient(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        await client.bootstrap()
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f'Kafka connection failed: {e}'
        ) from e
    finally:
        if client:
            await client.close()

    return {'status': 'ready'}
