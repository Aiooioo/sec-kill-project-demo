import random
from app.models.dto.dto_sales import ProductInventory


def mock_product_inventory(amount: int = 100):
    return [ProductInventory(
        product_id=round(random.random() * 10000 + 10 ** 7),
        stock=round(random.random() * 10),
        price=round(random.random() * 100, 2)
    ) for _ in range(amount)]
