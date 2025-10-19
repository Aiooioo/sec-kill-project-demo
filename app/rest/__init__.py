import logging
from fastapi import FastAPI

from contextlib import asynccontextmanager
from typing import Generic, TypeVar, Optional

from app.core.config import AppConfig
from app.models.http.base_response import SuccessResponse, ErrorResponse
from app.services.kafka_producer import init_kafka_producer, start_kafka_producer
from app.services.redis_service import get_redis_service
from app.mock.mock_products import mock_product_inventory

logger = logging.getLogger(__name__)

T = TypeVar('T')


def success_response(data: Optional[T] = None, message: str = '操作成功') -> SuccessResponse[T]:
    return SuccessResponse(code=200, data=data, message=message)


def error_response(code: int, message: str, error_detail: Optional[dict] = None) -> ErrorResponse:
    return ErrorResponse(code=code, message=message, err=error_detail)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('App service is starting...')

    init_kafka_producer(kafka_host=AppConfig.KAFKA_BOOTSTRAP_SERVERS)
    await start_kafka_producer()

    # TODO:
    # cache preload
    redis_service = get_redis_service()
    redis_service.preload(mock_product_inventory())

    logger.info('App service is ready...')

    yield

    logger.info('App service is stopped...')

    logger.info('App service is exiting...')
