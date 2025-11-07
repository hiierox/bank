
from typing import cast

import httpx
from fastapi import Depends, Request

from app.external_service.kafka_producer import KafkaProducerService
from app.logic.scoring import UserScoring


def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)


def get_kafka_producer_service(request: Request) -> KafkaProducerService:
    return cast(KafkaProducerService, request.app.state.kafka_producer)


def get_scoring_service(
    client: httpx.AsyncClient = Depends(get_http_client),
    kafka_producer: KafkaProducerService = Depends(get_kafka_producer_service)
) -> UserScoring:
    return UserScoring(client=client, kafka_producer=kafka_producer)
