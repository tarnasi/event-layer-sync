#!/usr/bin/env python3
"""
RabbitMQ Event Consumer
Run this script to consume events from RabbitMQ queues
"""

import sys
import logging
from app.core.rabbitmq import EventConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m app.consumer <queue_name>")
        print("Available queues: warehouse_events, shipment_events")
        sys.exit(1)
    
    queue_name = sys.argv[1]
    
    if queue_name not in ["warehouse_events", "shipment_events"]:
        print(f"Invalid queue name: {queue_name}")
        print("Available queues: warehouse_events, shipment_events")
        sys.exit(1)
    
    logger.info(f"Starting consumer for queue: {queue_name}")
    
    consumer = EventConsumer()
    
    try:
        consumer.start_consuming(queue_name)
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
        consumer.connection.disconnect()
    except Exception as e:
        logger.error(f"Consumer error: {e}")
        consumer.connection.disconnect()
        sys.exit(1)

if __name__ == "__main__":
    main()