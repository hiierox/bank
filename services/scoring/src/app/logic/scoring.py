import logging
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_fixed,
)

from app.api.scoring.schemas import (
    CreditHistoryItem,
    Product,
    PutUserData,
    UserData,
    UserProfileForDataService,
)
from app.config.config import Config
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
from app.core.custom_exceptions import LoanAlreadyExistsError, UserNotFoundError
from app.external_service.get_credit_status_service import get_credit_status

logger = logging.getLogger(__name__)


class UserScoring:
    def __init__(self, client: httpx.AsyncClient, config: Config):
        self.client = client
        self.retryer = AsyncRetrying(
            stop=stop_after_attempt(
                config.data_service.retries.max_attempts + 1
            ),
            wait=wait_fixed(config.data_service.retries.delay),
            retry=retry_if_exception_type(
                (httpx.TimeoutException, httpx.HTTPStatusError)
            ),
            reraise=True
        )

    async def user_scoring_pioneer(
        self,
        user_data: UserData,
        products: list[Product]
    ) -> dict[str, Any]:
        """
        Скоринг клиента и возврат доступного ему продукта
        """
        if (user_data.age < 18 or
            user_data.monthly_income < 1000000 or
                user_data.employment_type == 'unemployed'):
            return REJECT_RESPONSE

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
                user_data,
                best_eligible_product
            )
            try:
                response = await self.client.put(
                    '/user-data',
                    json=request_body.model_dump(mode='json')
                )
                if response.status_code == 201:
                    return {'decision': 'accepted', 'product': best_eligible_product}
                else:  # noqa: RET505
                    logger.error(
                        f"""Save User Error:
                        phone={user_data.phone},
                        status_code={response.status_code},
                        detail={response.text}"""
                    )
                    response.raise_for_status()
            except Exception as e:
                raise e

        return REJECT_RESPONSE

    async def user_scoring_repeater(self, phone: str, products: list[Product]
                                    ) -> dict[str, Any]:
        response = await self.client.get(f'/user-data?phone={phone}')
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
        user_profile = UserData.model_validate(user_dict)
        credit_history = [
            CreditHistoryItem.model_validate(
                item
            ) for item in user_profile_json['history']
        ]
        points = 0

        if credit_history:
            first_credit = credit_history[0]
            last_credit = credit_history[-1]
            last_credit_status = await get_credit_status(last_credit)

            if user_profile.age < 18:
                return REJECT_RESPONSE

            days_since_credit_issued = (
                datetime.now(tz=ZoneInfo('UTC')).date() -
                last_credit.issue_date
            ).days

            is_credit_open_more_than_180_days = (
                last_credit_status == 'open'
                and (days_since_credit_issued > 180)
            )

            if is_credit_open_more_than_180_days:
                return REJECT_RESPONSE

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
                user_profile,
                best_eligible_product
            )
            try:
                response = await self.client.put(
                    '/user-data',
                    json=request_body.model_dump(mode='json')
                )
                if response.status_code == 422:
                    raise LoanAlreadyExistsError
                response.raise_for_status()
                return {'decision': 'accepted', 'product': best_eligible_product}
            except Exception as e:
                logger.error(
                    f"""Update User or Loan Error:
                        phone={phone},
                        status_code={response.status_code},
                        detail={response.text}"""
                )
                raise e

        return REJECT_RESPONSE

    async def request_body_forming(
        self,
        phone: str,
        user_data: UserData,
        best_eligible_product: Product
    ) -> PutUserData:
        profile = UserProfileForDataService(
            age=user_data.age,
            monthly_income=user_data.monthly_income,
            employment_type=user_data.employment_type,
            has_property=user_data.has_property
        )
        loan_entry = CreditHistoryItem(
            loan_id=f'loan_{phone}_{datetime.now(
                tz=ZoneInfo('UTC')).strftime("%Y%m%d%H%M")}',
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
