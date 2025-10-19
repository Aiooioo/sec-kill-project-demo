import asyncio
import logging
import os

from app.consumer.order_consumer import init_kafka_consumer, place_user_orders

# 配置日志
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


async def main():
    try:
        # 确保在本地运行时使用正确的kafka地址
        # 如果没有设置环境变量，使用localhost:9092
        if not os.getenv('KAFKA_BOOTSTRAP_SERVERS'):
            os.environ['KAFKA_BOOTSTRAP_SERVERS'] = 'localhost:9092'
            logger.info("Using localhost:9092 as Kafka bootstrap server for local development")

        # 初始化kafka消费者
        logger.info("Initializing Kafka consumer...")
        await init_kafka_consumer()
        logger.info("Kafka consumer initialized successfully")

        # 创建并等待消费者任务
        # 使用asyncio.gather来确保任务能持续运行
        logger.info("Starting order processing task...")
        await place_user_orders()

    except Exception as e:
        logger.error(f"Error in consumer main: {str(e)}", exc_info=True)
    finally:
        logger.info("Consumer main function completed")


if __name__ == '__main__':
    logger.info("Starting Kafka consumer application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Consumer application stopped by keyboard interrupt")
    except Exception as e:
        logger.error(f"Fatal error in consumer application: {str(e)}", exc_info=True)
