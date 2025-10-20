from typing import Any

pioneer_products = [
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


class ProductRepository:
    """
    Репозиторий продуктов для клиентов
    """

    async def get_pioneer_products(self) -> list[dict[str, Any]]:
        """
        Возвращает список продуктов для новых клиентов
        """
        return pioneer_products
