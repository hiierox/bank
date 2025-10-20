from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from app.api.scoring.schemas import Product, UserData
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
from app.core.custom_exceptions import UserNotFoundError
from app.external_service.get_credit_status_service import get_credit_status
from app.repository.client_repo import ClientProfileRepository


class UserScoring:
    def __init__(self, client_repo: ClientProfileRepository):
        self.client_repo = client_repo

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
            await self.client_repo.save_user_profile(user_data)
            return {'decision': 'accepted', 'product': best_eligible_product}

        return REJECT_RESPONSE

    async def user_scoring_repeater(self, phone: str, products: list[Product]
                                    ) -> dict[str, Any]:
        user_profile = await self.client_repo.get_user_profile(phone)

        if not user_profile:
            raise UserNotFoundError

        points = 0

        if user_profile.credit_history:
            first_credit = user_profile.credit_history[0]
            last_credit = user_profile.credit_history[-1]
            last_credit_status = await get_credit_status(last_credit)

            if user_profile.user_data.age < 18:
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
            if age['min'] <= user_profile.user_data.age <= age['max']:
                points += age['points']
                break

        for income in INCOME_POINTS:
            if income['min'] <= user_profile.user_data.monthly_income <= income['max']:
                points += income['points']
                break

        for employment in EMPLOYMENT_TYPE:
            if user_profile.user_data.employment_type == employment['type']:
                points += employment['points']
                break

        if user_profile.user_data.has_property:
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
            if best_eligible_product is not None:
                await self.client_repo.save_user_credit_history(phone,
                                                                best_eligible_product)
                return {'decision': 'accepted', 'product': best_eligible_product}

        return REJECT_RESPONSE
