import redis
from app.core import config
from app.models.dto.dto_sales import ProductInventory
from app.constant.time import ONE_HOUR_IN_SECONDS


class RedisService:
    def __init__(self):
        redis_config = config.AppConfig.get_redis_config()

        self.client = redis.Redis(
            host=redis_config.get('host'),
            port=redis_config.get('port'),
            db=redis_config.get('db'),
            decode_responses=True
        )

    def preload(self, inventories: list[ProductInventory]) -> None:
        """
        缓存预热
        :param inventories: 商品信息
        """
        for product in inventories:
            # 设置一个用不过期的 key，存储商品剩余库存
            self.client.set(self._get_product_stock_key(product.product_id), product.stock)

    def get(self, key: str, level: str = "redis") -> str:
        return self.client.get(key)

    def set(self, key: str, value: str, expire: int = ONE_HOUR_IN_SECONDS, level: str = "redis") -> None:
        return self.client.set(key, value, expire)

    def invalidate(self, key: str, level: str = "redis") -> None:
        pass

    def exists(self, key: str, level: str = "redis") -> bool:
        return self.client.get(key) is not None

    def reduce(self, key: str, amount: int = 1):
        return self.client.decr(key, amount)

    def increase(self, key: str, amount: int = 1):
        return self.client.incr(key, amount)

    def _get_product_stock_key(self, product_id: int):
        return f'item:{product_id}:stock'

    def _get_product_sold_out_key(self, product_id: int):
        return f'item:{product_id}:sold_out'


def get_redis_service() -> RedisService:
    if not hasattr(get_redis_service, 'instance'):
        get_redis_service.instance = RedisService()

    return get_redis_service.instance
