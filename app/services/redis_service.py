import redis
from app.core import config


class RedisService:
    def __init__(self):
        redis_config = config.AppConfig.get_redis_config()

        self.client = redis.Redis(
            host=redis_config.get('host'),
            port=redis_config.get('port'),
            db=redis_config.get('db'),
            decode_responses=True
        )

    def preload(self):
        pass

    def get(self, key: str, level: str = "redis") -> str:
        pass

    def set(self, key: str, value: str, expire: int = 3600, level: str = "redis") -> None:
        pass

    def invalidate(self, key: str, level: str = "redis") -> None:
        pass


def get_redis_service() -> RedisService:
    if not hasattr(get_redis_service, 'instance'):
        get_redis_service.instance = RedisService()

    return get_redis_service.instance
