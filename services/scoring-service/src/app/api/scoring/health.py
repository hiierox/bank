from aiokafka import AIOKafkaClient
from fastapi import APIRouter, HTTPException
from httpx import AsyncClient

from app.config.config import settings

router = APIRouter()


@router.get('/up', status_code=200)
async def liveness_probe() -> dict[str, str]:
    return {'status': 'up'}


@router.get('/ready', status_code=200)
async def readiness_probe() -> dict[str, str]:
    kafka_client = None
    try:
        kafka_client = AIOKafkaClient(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        await kafka_client.bootstrap()
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f'Kafka connection failed {e}') from e
    finally:
        if kafka_client:
            await kafka_client.close()

    data_service_url = f'{settings.DATA_SERVICE_BASE_URL}/ready'

    async with AsyncClient() as client:
        response = await client.get(data_service_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=503, detail='user-data-service is not ready!'
            )
    return {'status': 'ready'}
