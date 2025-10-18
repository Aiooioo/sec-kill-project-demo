import logging
from fastapi import FastAPI

from contextlib import asynccontextmanager
from typing import Generic, TypeVar, Optional

from app.models.http.base_response import SuccessResponse, ErrorResponse

logger = logging.getLogger(__name__)


T = TypeVar('T')

def success_response(data: Optional[T] = None, message: str = '操作成功') -> SuccessResponse[T]:
    return SuccessResponse(code=200, data=data, message=message)


def error_response(code: int, message: str, error_detail: Optional[dict] = None) -> ErrorResponse:
    return ErrorResponse(code=code, message=message, err=error_detail)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('App service is starting...')

    # TODO:
    # cache preload

    logger.info('App service is ready...')

    yield

    logger.info('App service is stopped...')

    logger.info('App service is exiting...')