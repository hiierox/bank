class FlowService:
    def __init__(self, client_repo, product_repo):
        self.client_repo = client_repo
        self.product_repo = product_repo

    async def flow_type_selection(self, phone_number: str) -> dict:
        """
        Определение типа флоу для клиента и возврат подходящих данных
        """

        if await self.client_repo.is_number_known(phone_number):
            return {
                "flow_type": "repeater",
                "available_products": []
            }
        else:
            await self.client_repo.add_number(phone_number)
            return {
                "flow_type": "pioneer",
                "available_products": await self.product_repo.get_pioneer_products()
            }
