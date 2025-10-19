import logging
import time
from cachetools import TTLCache

from app.constant.time import ONE_MINUTE_IN_SECONDS, ONE_HOUR_IN_SECONDS
from app.services.redis_service import get_redis_service
from app.services.kafka_producer import send_order_message_async, send_sold_out_message_async

logger = logging.getLogger(__name__)


class FlashSalesService:
    sold_out_cache = TTLCache(maxsize=1000, ttl=ONE_MINUTE_IN_SECONDS * 10)

    def __init__(self):
        self.redis_service = get_redis_service()

    def check_l1_sold_out_state(self, product_id: int) -> bool:
        """
        检查本地内存 L1 缓存中的售罄状态。
        """

        is_sold_out = self.sold_out_cache.get(product_id)

        if is_sold_out == 'SOLD_OUT':
            return True

        return False

    def update_l1_sold_out_state(self, product_id: int):
        """
        更新本地内存 L1 缓存中的售罄状态。
        """
        self.sold_out_cache[product_id] = 'SOLD_OUT'

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
        sold_out_key = self._get_product_sold_out_key(product_id)

        try:
            # 1. 修正/回滚库存：将扣减多余的 quantity 加回来
            self.redis_service.increase(stock_key, quantity)

            # 2. 写入售罄 Key (TTL=1小时，作为熔断器的权威状态)
            self.redis_service.set(sold_out_key, "1", ONE_HOUR_IN_SECONDS)

            return 1
        except Exception as e:
            logger.info(f"Redis Service operation failed: {e}")
            return -9999

    async def flash_purchase(self, user_id: int, product_id: int, quantity: int = 1):
        try:

            # Step 1: L1 内存熔断检查
            if self.check_l1_sold_out_state(product_id):
                return {"err": "商品已售罄"}

            # Step 2: L1.5 Redis 熔断检查
            if self.redis_service.exists(self._get_product_sold_out_key(product_id)):
                return {"err": "商品已售罄"}

            # Step 3: 尝试库存预扣
            stock_maybe = self.check_and_decr_stock(product_id, quantity)

            if stock_maybe > 0:
                # 预扣成功，库存充足

                order_data = {
                    "item_id": product_id,

                    "user_id": user_id,

                    "quantity": quantity,

                    "time": time.time_ns() // 1000000
                }

                # Step 4: 异步发送下单消息到 Kafka (用于订单落地)
                await send_order_message_async(topic="product_orders", message=order_data)

                return {"success": True, "message": "抢购成功，订单正在处理中！", "current_stock": stock_maybe}

            else:
                # 扣减失败，但售罄 Key 已写入 Redis

                # Step 4: 发送售罄状态消息到 Kafka (用于通知所有实例更新 L1 熔断状态)
                await send_sold_out_message_async(item_id=product_id)

                self.rollback_stock(product_id, quantity)

                return {"err": "商品库存不足"}
        except Exception as e:
            logger.info(f"Flash purchase error: {e}")
            return {"err": "系统异常"}

    def _get_product_stock_key(self, product_id: int):
        return f'item:{product_id}:stock'

    def _get_product_sold_out_key(self, product_id: int):
        return f'item:{product_id}:sold_out'


def get_flash_sales_service():
    if not hasattr(get_flash_sales_service, 'instance'):
        get_flash_sales_service.instance = FlashSalesService()

    return get_flash_sales_service.instance
