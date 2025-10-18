
from pydantic import BaseModel, Field

class UserPurchaseRequest(BaseModel):
    user_id: int = Field(..., description="User ID")

    amount: int = Field(..., description="Product amount in this purchase")

    model_config = {
        "extra": "forbid",

        "str_strip_whitespace": True
    }
