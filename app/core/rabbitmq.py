import pika
import json
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class RabbitMQConnection:
    def __init__(self, host='localhost', port=5672, username='guest', password='guest'):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection = None
        self.channel = None
        
    def connect(self):
        try:
            credentials = pika.PlainCredentials(self.username, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                credentials=credentials
            )
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare exchange and queues
            self.channel.exchange_declare(exchange='logistic_events', exchange_type='topic')
            self.channel.queue_declare(queue='warehouse_events', durable=True)
            self.channel.queue_declare(queue='shipment_events', durable=True)
            
            # Bind queues to exchange
            self.channel.queue_bind(exchange='logistic_events', queue='warehouse_events', routing_key='warehouse.*')
            self.channel.queue_bind(exchange='logistic_events', queue='shipment_events', routing_key='shipment.*')
            
            logger.info("Connected to RabbitMQ successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def disconnect(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    def publish_event(self, routing_key: str, event_data: Dict[str, Any], operation_name: str):
        if not self.channel:
            if not self.connect():
                logger.error("Cannot publish event: No RabbitMQ connection")
                return False
        
        try:
            message = {
                "operation_name": operation_name,
                "event_data": event_data,
                "timestamp": datetime.utcnow().isoformat(),
                "routing_key": routing_key
            }
            
            self.channel.basic_publish(
                exchange='logistic_events',
                routing_key=routing_key,
                body=json.dumps(message),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    headers={"operation-name": operation_name}
                )
            )
            logger.info(f"Published event: {routing_key} with operation: {operation_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            return False

# Global RabbitMQ connection instance
rabbitmq = RabbitMQConnection()


class EventProducer:
    @staticmethod
    def warehouse_created(warehouse_data: Dict[str, Any], operation_name: str):
        return rabbitmq.publish_event("warehouse.created", warehouse_data, operation_name)
    
    @staticmethod
    def warehouse_updated(warehouse_data: Dict[str, Any], operation_name: str):
        return rabbitmq.publish_event("warehouse.updated", warehouse_data, operation_name)
    
    @staticmethod
    def warehouse_deleted(warehouse_data: Dict[str, Any], operation_name: str):
        return rabbitmq.publish_event("warehouse.deleted", warehouse_data, operation_name)
    
    @staticmethod
    def shipment_created(shipment_data: Dict[str, Any], operation_name: str):
        return rabbitmq.publish_event("shipment.created", shipment_data, operation_name)
    
    @staticmethod
    def shipment_updated(shipment_data: Dict[str, Any], operation_name: str):
        return rabbitmq.publish_event("shipment.updated", shipment_data, operation_name)
    
    @staticmethod
    def shipment_deleted(shipment_data: Dict[str, Any], operation_name: str):
        return rabbitmq.publish_event("shipment.deleted", shipment_data, operation_name)


class EventConsumer:
    def __init__(self):
        self.connection = RabbitMQConnection()
    
    def start_consuming(self, queue_name: str):
        if not self.connection.connect():
            logger.error("Cannot start consuming: No RabbitMQ connection")
            return
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                operation_name = message.get("operation_name", "unknown")
                event_data = message.get("event_data", {})
                routing_key = message.get("routing_key", "")
                
                logger.info(f"Received event: {routing_key} with operation: {operation_name}")
                logger.info(f"Event data: {event_data}")
                
                # Process the event here
                self.process_event(routing_key, event_data, operation_name)
                
                # Acknowledge the message
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.connection.channel.basic_consume(queue=queue_name, on_message_callback=callback)
        logger.info(f"Started consuming from queue: {queue_name}")
        self.connection.channel.start_consuming()
    
    def process_event(self, routing_key: str, event_data: Dict[str, Any], operation_name: str):
        """Process the received event - implement your business logic here"""
        if routing_key.startswith("warehouse."):
            logger.info(f"Processing warehouse event: {operation_name}")
        elif routing_key.startswith("shipment."):
            logger.info(f"Processing shipment event: {operation_name}")
        else:
            logger.info(f"Processing unknown event: {operation_name}")