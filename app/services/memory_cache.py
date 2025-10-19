import logging
import asyncio
from typing import Optional

from cachetools import TTLCache

from app.constant.time import ONE_MINUTE_IN_SECONDS
from app.services import kafka_consumer

logger = logging.getLogger(__name__)


class MemoryCache:
    memory_storage: TTLCache = TTLCache(maxsize=1000, ttl=ONE_MINUTE_IN_SECONDS * 10)

    def get_value(self, key):
        return self.memory_storage.get(key)

    def set_value(self, key, value):
        self.memory_storage[key] = value

    async def start_sync_loop_from_kafka(self):

        if not kafka_consumer.kafka_consumer:
            raise ConnectionError("Kafka consumer is not initialized")

        await kafka_consumer.kafka_consumer.start()

        try:
            async for msg in kafka_consumer.kafka_consumer:
                logger.info(f"Received message from Kafka: {msg.value}")

                item_id = msg.value.get("item_id")
                status = msg.value.get("status")

                if item_id and status == "SOLD_OUT":
                    self.set_value(f"product_sold_out_{item_id}", "SOLD_OUT")

                    logger.info(f"Product {item_id} is marked as sold out in memory cache.")
        finally:
            await kafka_consumer.kafka_consumer.stop()


memory_cache: Optional[MemoryCache] = None


def init_memory_cache():
    global memory_cache
    memory_cache = MemoryCache()
    asyncio.create_task(memory_cache.start_sync_loop_from_kafka())
