from pydantic import BaseModel, Field
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseResponse(BaseModel):

    code: int = Field(..., description="API Response Code")

    message: str = Field(..., description="API Response Message")

class SuccessResponse(BaseResponse, Generic[T]):
    """
    请求成功响应模型，包括数据字段
    """
    data: Optional[T] = Field(None, description="API Response Data")

class ErrorResponse(BaseResponse):
    """
    请求失败响应模型，包括错误信息
    """
    err: Optional[dict] = Field(None, description="API Response Error")