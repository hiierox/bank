
from pathlib import Path
from typing import cast

import httpx
from fastapi import Depends, Request

from app.config.config import Config
from app.logic.scoring import UserScoring


def get_config() -> Config:
    config_path = Path(__file__).parent.parent / 'config' / 'config.yaml'
    return Config.from_yaml(config_path)


def get_http_client(request: Request) -> httpx.AsyncClient:
    return cast(httpx.AsyncClient, request.app.state.http_client)


def get_scoring_service(
    client: httpx.AsyncClient = Depends(get_http_client),
    config: Config = Depends(get_config)
) -> UserScoring:
    return UserScoring(client=client, config=config)
