import os
import time
import json
import logging
import asyncio

from aiokafka import AIOKafkaProducer

logger = logging.getLogger(__name__)

kafka_producer: AIOKafkaProducer = None


def init_kafka_producer(kafka_host: str):
    global kafka_producer

    kafka_producer = AIOKafkaProducer(
        bootstrap_servers=kafka_host,
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        loop=asyncio.get_event_loop(),
        acks=1  # 确保消息至少被写入 Leader
    )


async def start_kafka_producer():
    if kafka_producer:
        await kafka_producer.start()


async def stop_kafka_producer():
    if kafka_producer:
        await kafka_producer.stop()


async def send_order_message_async(topic: str, message: dict):
    if not kafka_producer:
        raise ConnectionError("Kafka producer is not initialized")

    # 异步发送，不等待 Broker 响应 (高性能的关键)
    future = await kafka_producer.send(topic, message)

    return future


async def send_sold_out_message_async(item_id: int):
    message = {"item_id": item_id, "status": "SOLD_OUT", "timestamp": time.time()}

    await kafka_producer.send("product_status_change_topic", message)
