from typing import Any

PIONEER_PRODUCTS = [
    {
        'name': 'MicroLoan',
        'amount': '30000',
        'percentage': '15'
    },
    {
        'name': 'QuickMoney',
        'amount': '60000',
        'percentage': '10'
    },
    {
        'name': 'ConsumerLoan',
        'amount': '120000',
        'percentage': '10'
    }
]
REPEATER_PRODUCTS = [
    {
        'name': 'LoyaltyLoan',
        'amount': '5000000',
        'percentage': '1.8'},
    {
        'name': 'AdvantagePlus',
        'amount': '12000000',
        'percentage': '1.6'},
    {
        'name': 'PrimeCredit',
        'amount': '50000000',
        'percentage': '1.4'},
]


class ProductRepository:
    """
    Репозиторий продуктов для клиентов
    """

    async def get_pioneer_products(self) -> list[dict[str, Any]]:
        """
        Возвращает список продуктов для новых клиентов
        """
        return PIONEER_PRODUCTS

    async def get_repeater_products(self) -> list[dict[str, Any]]:
        """
        Возвращает список продуктов для повторных клиентов
        """
        return REPEATER_PRODUCTS
