from typing import Any

from app.api.scoring.schemas import Product, UserData
from app.core.constants import (
    AGE_POINTS_RULES,
    EMPLOYMENT_TYPE,
    INCOME_POINTS,
    PRODUCTS_POINTS,
    REJECT_RESPONSE,
)
from app.repository.client_repo import ClientProfileRepository


class UserScoring:
    def __init__(self, client_repo: ClientProfileRepository):
        self.client_repo = client_repo

    async def user_scoring(
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
            for pioneer_product in PRODUCTS_POINTS:
                if (user_product.name == pioneer_product['name'] and
                        pioneer_product['min'] <= points <= pioneer_product['max']):
                    eligible_products[pioneer_product['min']] = user_product

        if eligible_products:
            best_eligible_product = eligible_products.get(max(eligible_products.keys()))
            await self.client_repo.save_user_profile(user_data)
            return {'decision': 'accepted', 'product': best_eligible_product}

        return REJECT_RESPONSE
