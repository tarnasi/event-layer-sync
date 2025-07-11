#!/usr/bin/env python3
"""
Distributed RabbitMQ Event Consumer
Run this script to consume events from other servers in the distributed system
"""

import sys
import logging
from app.core.rabbitmq import DistributedEventConsumer
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    logger.info(f"Starting distributed consumer for server {settings.SERVER_ID}")
    logger.info(f"Will consume events from servers: {settings.ALLOWED_SERVERS}")
    
    consumer = DistributedEventConsumer()
    
    try:
        consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
        consumer.connection.disconnect()
    except Exception as e:
        logger.error(f"Consumer error: {e}")
        consumer.connection.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    main()