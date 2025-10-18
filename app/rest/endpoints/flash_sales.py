import logging
from fastapi import APIRouter, Body, Path, HTTPException, Depends

from app.services.redis_service import RedisService, get_redis_service
from app.models.dto.dto_sales import UserPurchaseRequest
from app.models.http.base_response import SuccessResponse
from app.rest import success_response

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get('/')
async def root():
    logger.info('App root endpoint accessed')

    return {
        "message": "This is a demo project for the simple data flow in flash sales scenarios.",
        "version": "0.0.1"
    }


@router.get('/purchase', response_model=SuccessResponse[bool])
async def purchase(
    request: UserPurchaseRequest = Body(...),
    redis_service: RedisService = Depends(get_redis_service)
):
    try:

    except:
        raise HTTPException(status_code=500)

    return success_response(data=True)
