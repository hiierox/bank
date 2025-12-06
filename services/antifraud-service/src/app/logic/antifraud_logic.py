from datetime import date, datetime
from zoneinfo import ZoneInfo

from app.api.antifraud.schemas import (
    AntifraudDecisionResponse,
    PioneerCheckRequest,
    RepeaterCheckRequest,
)
from app.external_services.data_service.logic.data_service import DataService
from app.external_services.redis_service.redis_service import RedisService
from app.logic.check_rules import (
    CommonChecks,
    PioneerChecks,
    RepeaterChecks,
)


class AntifraudService:
    """
    Отвечает за вызов внешних сервисов (redis, data), запуск проверок и
    вывод результатов.
    """

    def __init__(self, data_service: DataService, redis_service: RedisService):
        self.data_service = data_service
        self.redis_service = redis_service

    def _get_current_date(self) -> date:
        """Получает текущую дату в UTC"""
        return datetime.now(tz=ZoneInfo('UTC')).date()

    async def _process_checks(
            self, reasons: list[str], phone: str
        ) -> AntifraudDecisionResponse:
        """
        Общая логика агрегации результатов
        """
        final_reasons = [r for r in reasons if r is not None]

        if final_reasons:
            return AntifraudDecisionResponse(
                decision='rejected',
                reasons=final_reasons
            )

        await self.redis_service.increment_application_count(phone)

        return AntifraudDecisionResponse(
            decision='passed',
            reasons=[]
        )

    async def check_pioneer(
            self,
            request: PioneerCheckRequest
        ) -> AntifraudDecisionResponse:
        """Обрабатывает антифрод проверки для pioneer"""
        user_data = request.user_data
        phone = user_data.phone

        application_count = await self.redis_service.get_application_count(phone)

        all_reasons = []
        all_reasons.extend(CommonChecks.run(user_data))
        all_reasons.extend(PioneerChecks.run(
            user_data=user_data,
            application_count=application_count
        ))

        return await self._process_checks(all_reasons, phone)


    async def check_repeater(
            self,
            request: RepeaterCheckRequest
        ) -> AntifraudDecisionResponse:
        """Обрабатывает антифрод проверки для repeater"""
        new_updated_profile = request.new_updated_profile
        phone = request.phone
        current_date = self._get_current_date()

        data_service_response = await self.data_service.get_user_profile(phone)

        all_reasons = []
        all_reasons.extend(CommonChecks.run(new_updated_profile))
        all_reasons.extend(RepeaterChecks.run(
            new_updated_profile=new_updated_profile,
            data_service_response=data_service_response,
            check_date=current_date
        ))

        return await self._process_checks(all_reasons, phone)
