import logging
from fastapi import APIRouter, Path, HTTPException

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get('/')
async def root():
    logger.info('App root endpoint accessed')

    return {
        "message": "This is a demo project for the simple data flow in flash sales scenarios.",
        "version": "0.0.1"
    }