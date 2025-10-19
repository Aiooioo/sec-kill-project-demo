import json
import logging
import asyncio

from aiokafka import AIOKafkaConsumer
from typing import Optional

logger = logging.getLogger(__name__)

kafka_consumer: Optional[AIOKafkaConsumer] = None


def init_kafka_consumer(kafka_host: str, topic: str, group_id: str):
    global kafka_consumer

    loop = asyncio.get_event_loop()

    kafka_consumer = AIOKafkaConsumer(
        topic,
        loop=loop,
        bootstrap_servers=kafka_host,
        group_id=group_id,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest'  # 从最新的消息开始消费
    )
