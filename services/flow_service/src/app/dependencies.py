
from pathlib import Path
from typing import cast

import httpx
from fastapi import Depends, Request

from app.config.config import Config
from app.logic.flow_service import FlowService
from app.repository.product_repo import ProductRepository


def get_config() -> Config:
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    return Config.from_yaml(config_path)


def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)


def get_product_repo() -> ProductRepository:
    return ProductRepository()


def get_flow_service(
    product_repo: ProductRepository = Depends(get_product_repo),
    client: httpx.AsyncClient = Depends(get_http_client),
    config: Config = Depends(get_config)
) -> FlowService:
    return FlowService(
        product_repo=product_repo,
        client=client,
        config=config
    )
