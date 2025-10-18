import logging
from fastapi import APIRouter, Body, Path, HTTPException, Depends

from app.services.sales.flash_sales_service import FlashSalesService, get_flash_sales_service
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
        flash_sales_service: FlashSalesService = Depends(get_flash_sales_service)
):
    try:
        flash_sales_service.flash_purchase(request.user_id, request.product_id, request.amount)
    except:
        raise HTTPException(status_code=500)

    return success_response(data=True)
