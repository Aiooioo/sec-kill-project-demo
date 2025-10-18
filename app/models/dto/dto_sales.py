from pydantic import BaseModel, Field


class UserPurchaseRequest(BaseModel):
    """
    用户抢购下单请求结构
    """

    user_id: int = Field(..., description="User ID")

    product_id: int = Field(..., description="Product ID")

    amount: int = Field(..., description="Product amount in this purchase")

    model_config = {
        "extra": "forbid",

        "str_strip_whitespace": True
    }


class ProductInventory(BaseModel):
    """
    商品库存 L3 存储结构
    """

    product_id: int = Field(..., description="Product ID")

    price: float = Field(..., description="Product price")

    stock: int = Field(..., description="Product stock")
