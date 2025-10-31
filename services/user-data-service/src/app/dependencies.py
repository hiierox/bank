from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_async_session
from app.logic.data_service import UserDataService


def get_user_data_service(
    session: AsyncSession = Depends(get_async_session)
) -> UserDataService:
    """
    Возращает сервис данных c новой сессией для каждого HTTP запроса
    """
    return UserDataService(session)
