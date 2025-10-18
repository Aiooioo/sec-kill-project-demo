import logging
import time
from app.services.redis_service import get_redis_service

logger = logging.getLogger(__name__)


class FlashSalesService:

    def __init__(self):
        self.redis_service = get_redis_service()

    def check_and_decr_stock(self, product_id: int, quantity: int):
        """
        [原子化操作]
        尝试通过 Redis 扣减指定的商品个数
        :return:
        """

        stock_key = self._get_product_stock_key(product_id)

        try:
            stock_maybe = self.redis_service.reduce(stock_key, quantity)

            return stock_maybe
        except Exception as e:
            logger.info(f"Redis Service operation failed: {e}")
            return -9999

    def rollback_stock(self, product_id: int, quantity: int):
        """
        [原子化操作]
        尝试通过 Redis 恢复指定的商品个数
        :return:
        """

        stock_key = self._get_product_stock_key(product_id)

        try:
            stock_maybe = self.redis_service.increase(stock_key, quantity)

            return stock_maybe
        except Exception as e:
            logger.info(f"Redis Service operation failed: {e}")
            return -9999

    def flash_purchase(self, user_id: int, product_id: int, quantity: int = 1):
        try:
            stock_maybe = self.check_and_decr_stock(product_id, quantity)

            if stock_maybe > 0:
                order_data = {
                    "item_id": product_id,

                    "user_id": user_id,

                    "quantity": quantity,

                    "time": time.time()
                }


            else:
                self.rollback_stock(product_id, quantity)

                return {"err": "商品库存不足"}
        except Exception as e:
            logger.info(f"Flash purchase error: {e}")
            return {"err": "系统异常"}

    def _get_product_stock_key(self, product_id: int):
        return f'item:{product_id}:stock'


def get_flash_sales_service():
    if not hasattr(get_flash_sales_service, 'instance'):
        get_flash_sales_service.instance = FlashSalesService()

    return get_flash_sales_service.instance
