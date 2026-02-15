import logging
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from aiokafka.errors import KafkaError

from app.api.scoring.schemas import (
    AntifraudCheckResponse,
    CreditHistoryItem,
    Product,
    PutUserData,
    UserData,
    UserDataFromDataService,
    UserProfileForDataService,
)
from app.core.constants import (
    AGE_POINTS_RULES,
    EMPLOYMENT_TYPE,
    FIRST_CREDIT_AGE_DAYS,
    FIRST_CREDIT_POINTS,
    INCOME_POINTS,
    LAST_CREDIT_AMOUNT_POINTS,
    PIONEER_PRODUCTS_POINTS,
    REJECT_RESPONSE,
    REPEATER_PRODUCTS_POINTS,
)
from app.core.custom_exceptions import IntegrationError, UserNotFoundError
from app.external_service.antifraud_service import AntifraudService
from app.external_service.kafka_producer import KafkaProducerService

logger = logging.getLogger(__name__)


class UserScoring:
    def __init__(
        self,
        client: httpx.AsyncClient,
        kafka_producer: KafkaProducerService,
        antifraud_service: AntifraudService
    ):
        self.client = client
        self.kafka_producer = kafka_producer
        self.antifraud_service = antifraud_service

    async def _send_kafka_event(
        self,
        event_type: str,
        request_body: PutUserData
    ) -> None:
        """Формирует и отправляет событие в Kafka."""
        profile_data = request_body.profile
        phone = request_body.phone
        loan_entry = request_body.loan_entry

        message = {
            'version': 1,
            'occurred_at': datetime.now(tz=ZoneInfo('UTC')).isoformat(),
            'phone': phone,
            'event': event_type,
            'profile': profile_data.model_dump(mode='json') if profile_data else None,
            'history_entry': loan_entry.model_dump(mode='json')
        }
        try:
            logger.info(f'Preparing to send kafka event: {event_type}')
            await self.kafka_producer.send(key=phone, value=message)
        except KafkaError:
            logger.exception(f'Failed to send kafka event for phone {phone}')



    async def user_scoring_pioneer(
        self,
        user_data: UserData,
        products: list[Product]
    ) -> dict[str, Any]:
        """
        Скоринг клиента и возврат доступного ему продукта
        """
        try:
            antifraud_response_dict = await self.antifraud_service.check_pioneer(
                user_data
                )
            antifraud_response = AntifraudCheckResponse.model_validate(
                antifraud_response_dict
                )
        except IntegrationError as e:
            logger.error(f'Антифрод ошибка: {e}')
            raise e

        if antifraud_response.decision == 'rejected':
            logger.info(f'Антифрод не пройден. Причины: {antifraud_response.reasons}')
            return REJECT_RESPONSE
        logger.info('Атифрод успешно пройден')

        points = 0

        for age in AGE_POINTS_RULES:
            if age['min'] <= user_data.age <= age['max']:
                points += age['points']
                break

        for income in INCOME_POINTS:
            if income['min'] <= user_data.monthly_income <= income['max']:
                points += income['points']
                break

        for employment in EMPLOYMENT_TYPE:
            if user_data.employment_type == employment['type']:
                points += employment['points']
                break

        if user_data.has_property:
            points += 2

        eligible_products = {}
        for user_product in products:
            for pioneer_product in PIONEER_PRODUCTS_POINTS:
                if (user_product.name == pioneer_product['name'] and
                        pioneer_product['min'] <= points):
                    eligible_products[pioneer_product['min']] = user_product

        if eligible_products:
            best_eligible_product = eligible_products.get(
                max(eligible_products.keys()))
            if best_eligible_product is None:
                return REJECT_RESPONSE

            request_body = await self.request_body_forming(
                user_data.phone,
                best_eligible_product,
                user_data
            )
            await self._send_kafka_event(
                event_type='pioneer_accepter',
                request_body=request_body
            )
            return {'decision': 'accepted', 'product': best_eligible_product}

        return REJECT_RESPONSE

    async def user_scoring_repeater(self, phone: str, products: list[Product]
                                    ) -> dict[str, Any]:
        try:
            response = await self.client.get(f'/user-data?phone={phone}')
        except httpx.RequestError as e:
            raise Exception('user-data-service network error') from e


        if response.status_code == 404:
            logger.error(
                f"""UserNotFoundError:
                        /user-data?phone={phone},
                        status_code={response.status_code},
                        detail={response.text}"""
            )
            raise UserNotFoundError
        if response.status_code != 200:
            logger.error(
                f"""UnexpectedError:
                        /user-data?phone={phone},
                        status_code={response.status_code},
                        detail={response.text}"""
            )
            raise Exception

        user_profile_json = response.json()
        user_dict = user_profile_json['profile']
        user_dict['phone'] = user_profile_json['phone']
        user_profile = UserDataFromDataService.model_validate(user_dict)
        credit_history = [
            CreditHistoryItem.model_validate(
                item
            ) for item in user_profile_json['history']
        ]

        logger.info('Заход в антифрод')
        try:
            antifraud_response_dict = await self.antifraud_service.check_repeater(
                phone=phone,
                new_updated_profile=user_profile
            )
            antifraud_response = AntifraudCheckResponse.model_validate(
                antifraud_response_dict
                )
        except IntegrationError as e:
            logger.error(f'Антифрод ошибка: {e}')
            raise e
        except Exception as e:
            logger.error(f'Что-то произошло в вызове антифрода: {e}')
            raise e

        if antifraud_response.decision == 'rejected':
            logger.info(f'Антифрод не пройден. Причины: {antifraud_response.reasons}')
            return REJECT_RESPONSE
        logger.info('Антифрод успешно пройден')

        points = 0

        if credit_history:
            first_credit = credit_history[0]
            last_credit = credit_history[-1]

            if (datetime.now(tz=ZoneInfo('UTC')).date() - first_credit.issue_date >
                    timedelta(days=FIRST_CREDIT_AGE_DAYS)):
                points += FIRST_CREDIT_POINTS

            for last_amount in LAST_CREDIT_AMOUNT_POINTS:
                if last_amount['min'] <= last_credit.amount <= last_amount['max']:
                    points += last_amount['points']
                    break

        for age in AGE_POINTS_RULES:
            if age['min'] <= user_profile.age <= age['max']:
                points += age['points']
                break

        for income in INCOME_POINTS:
            if income['min'] <= user_profile.monthly_income <= income['max']:
                points += income['points']
                break

        for employment in EMPLOYMENT_TYPE:
            if user_profile.employment_type == employment['type']:
                points += employment['points']
                break

        if user_profile.has_property:
            points += 2

        eligible_products = {}
        for user_product in products:
            for repeater_product in REPEATER_PRODUCTS_POINTS:
                if (user_product.name == repeater_product['name'] and
                        repeater_product['min'] <= points):
                    eligible_products[repeater_product['min']] = user_product

        if eligible_products:
            best_eligible_product = eligible_products.get(
                max(eligible_products.keys()))
            if best_eligible_product is None:
                return REJECT_RESPONSE

            request_body = await self.request_body_forming(
                phone,
                best_eligible_product
            )

            await self._send_kafka_event(
                event_type='repetaer_accepted',
                request_body=request_body
            )
            return {'decision': 'accepted', 'product': best_eligible_product}

        return REJECT_RESPONSE

    async def request_body_forming(
        self,
        phone: str,
        best_eligible_product: Product,
        user_data: UserData | None = None,
    ) -> PutUserData:
        if user_data:
            profile = UserProfileForDataService(
                age=user_data.age,
                monthly_income=user_data.monthly_income,
                employment_type=user_data.employment_type,
                has_property=user_data.has_property
            )
        else:
            profile = None

        loan_entry = CreditHistoryItem(
            loan_id=f'loan_{phone}_{datetime.now(
                tz=ZoneInfo('UTC')).strftime("%Y%m%d%H%M%S")}',
            product_name=best_eligible_product.name,
            amount=best_eligible_product.max_amount,
            issue_date=datetime.now(
                tz=ZoneInfo('UTC')).date(),
            term_days=best_eligible_product.term_days,
            status='open',
            close_date=None
        )
        return PutUserData(
            phone=phone,
            profile=profile,
            loan_entry=loan_entry
        )
