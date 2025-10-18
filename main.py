import os
import logging
from fastapi import FastAPI, applications
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware

from starlette.staticfiles import StaticFiles

from app.rest import lifespan
from app.rest.endpoints import flash_sales

fastapi_app: FastAPI | None = None

allowed_origins = ["*"]

os.makedirs('logs', exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join('logs', 'app.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

logger.info(f"App Start - FlashSales v0.0.1")
logger.info(f"Debug Mode: {os.getenv('DEBUG', 'False').lower() == 'true'}")
logger.info(f"Log Level: INFO")
logger.info(f"Log File: {os.path.join('logs', 'app.log')}")


def custom_swagger_ui_html(*args, **kwargs):
    return get_swagger_ui_html(
        *args,
        **kwargs,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css"
    )


def init_rest_api():
    global fastapi_app

    applications.get_swagger_ui_html = custom_swagger_ui_html
    fastapi_app = FastAPI(
        title='Flash Sales',
        description="Flash Sales demo app",
        version='0.0.1',
        lifespan=lifespan
    )

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")

    fastapi_app.include_router(flash_sales.router, tags=["flash_sales"])


def main():
    """
    应用初始化
    """

    init_rest_api()


main()
