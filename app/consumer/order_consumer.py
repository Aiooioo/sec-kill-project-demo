import os
import json
import time
import logging
import asyncio
from asyncio import create_task

from typing import Optional

from aiokafka import AIOKafkaConsumer
from app.core.config import AppConfig

logger = logging.getLogger(__name__)

kafka_consumer: Optional[AIOKafkaConsumer] = None

SUCCESSFUL_ORDERS_COUNT = 0
FAILED_ORDERS_COUNT = 0

async def init_kafka_consumer():
    global kafka_consumer

    try:
        # 获取当前事件循环
        loop = asyncio.get_event_loop()
        
        # 记录连接信息
        logger.info(f"Connecting to Kafka at {AppConfig.KAFKA_BOOTSTRAP_SERVERS}")
        logger.info(f"Consumer group: flash_customers_group")
        logger.info(f"Topic: product_orders")

        kafka_consumer = AIOKafkaConsumer(
            "product_orders",
            loop=loop,
            bootstrap_servers=AppConfig.KAFKA_BOOTSTRAP_SERVERS,
            group_id="flash_customers_group",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset="earliest"  # 从最早的消息开始消费，确保不丢失消息
        )

        # 启动消费者
        await kafka_consumer.start()
        logger.info("Kafka consumer started successfully")
        
        # 尝试获取消费者分配的分区，验证连接是否正常
        try:
            partitions = kafka_consumer.assignment()
            if partitions:
                logger.info(f"Successfully connected to Kafka. Assigned partitions: {partitions}")
            else:
                logger.warning("Connected to Kafka but no partitions assigned. This might indicate topic doesn't exist yet.")
        except Exception as e:
            logger.warning(f"Connected to Kafka but failed to get partitions: {str(e)}")
            
    except Exception as e:
        logger.error(f"Failed to initialize Kafka consumer: {str(e)}", exc_info=True)
        raise


async def persist_order_to_db(order_data: dict) -> bool:
    global SUCCESSFUL_ORDERS_COUNT
    global FAILED_ORDERS_COUNT

    await asyncio.sleep(0.05)

    if order_data.get("user_id") % 10 != 0:
        SUCCESSFUL_ORDERS_COUNT += 1
        logger.info(
            f"[DB SUCCESS] Order {SUCCESSFUL_ORDERS_COUNT}: User {order_data['user_id']} purchase item {order_data['item_id']}")

        return True
    else:
        FAILED_ORDERS_COUNT += 1
        logger.info(
            f"[DB FAILED] Order {FAILED_ORDERS_COUNT}: Failed to persist order for User {order_data['user_id']}")
        return False


async def place_user_orders():
    if kafka_consumer is None:
        logger.error("Kafka consumer is not initialized, cannot start processing orders")
        return

    try:
        logger.info("Starting to consume messages from Kafka topic 'product_orders'")
        
        # 持续消费消息
        async for msg in kafka_consumer:
            try:
                order_data = msg.value
                
                # 验证消息格式
                if not isinstance(order_data, dict) or 'user_id' not in order_data:
                    logger.error(f"Invalid message format: {order_data}")
                    continue
                    
                logger.info(f"[KAFKA] Received order offset {msg.offset} for user: {order_data['user_id']}")

                item_id = msg.value.get("item_id")
                user_id = msg.value.get("user_id")
                quantity = msg.value.get("quantity")

                # 创建任务处理订单
                asyncio.create_task(persist_order_to_db(order_data))

                print(
                    f"Place user order into the persist DB. User ID is {user_id}. Product ID is {item_id}. User amount is {quantity}")
            
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON message: {msg.value}")
            except KeyError as e:
                logger.error(f"Missing required field in order data: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing message: {str(e)}", exc_info=True)

    except asyncio.CancelledError:
        logger.info("Consumer Task cancelled")
    except ConnectionError as e:
        logger.error(f"Kafka connection error: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error in consumer: {str(e)}", exc_info=True)
    finally:
        try:
            if kafka_consumer:
                logger.info("Stopping Kafka consumer...")
                await kafka_consumer.stop()
                logger.info("Kafka Consumer stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping Kafka consumer: {str(e)}")
