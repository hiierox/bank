from app.api.products.schemas import Product
pioneer_products = [
                    {
                    'name': 'Кредит Базовый',
                    'amount': 'от 10 000 до 20 000',
                    'percentage': '15%'
                    },
                    {
                    'name': 'Кредит Средний',
                    'amount': 'от 50 000 до 100 000',
                    'percentage': '12%'
                    },
                    {
                    'name': 'Кредит Большой',
                    'amount': 'от 100 000 до 1 000 000',
                    'percentage': '10%'
                    }
                ]


class ProductRepository:
    """
    Репозиторий продуктов для клиентов
    """
    
    async def get_pioneer_products(self) -> list[Product]:
        """
        Возвращает список продуктов для новых клиентов
        """
        return pioneer_products