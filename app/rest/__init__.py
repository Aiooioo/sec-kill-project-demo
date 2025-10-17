from typing import Generic, TypeVar, Optional
from app.models.http.base_response import SuccessResponse, ErrorResponse

T = TypeVar('T')


def success_response(data: Optional[T] = None, message: str = '操作成功') -> SuccessResponse[T]:
    return SuccessResponse(code=200, data=data, message=message)


def error_response(code: int, message: str, error_detail: Optional[dict] = None) -> ErrorResponse:
    return ErrorResponse(code=code, message=message, err=error_detail)
