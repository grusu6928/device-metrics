"""Kafka consumer main entry point"""

import asyncio
import logging

from src.consumer.consumer import MetricsConsumer

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    """Main consumer loop"""
    consumer = MetricsConsumer()

    try:
        await consumer.start()
        logger.info("Metrics consumer started")

        # Run forever
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(main())
