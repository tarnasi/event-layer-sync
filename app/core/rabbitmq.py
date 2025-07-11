import pika
import json
import logging
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
from app.core.config import settings

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
        """Establish connection to RabbitMQ with authentication"""
        try:
            # Create connection parameters with authentication
            credentials = pika.PlainCredentials(
                username=settings.RABBITMQ_USERNAME,
                password=settings.RABBITMQ_PASSWORD
            )
            
            parameters = pika.ConnectionParameters(
                host=settings.RABBITMQ_HOST,
                port=settings.RABBITMQ_PORT,
                virtual_host=settings.RABBITMQ_VIRTUAL_HOST,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare the exchange for distributed events
            self.channel.exchange_declare(
                exchange='distributed_events',
                exchange_type='topic',
                durable=True
            )
            
            # Declare queue for this server
            queue_name = f"server_{settings.SERVER_ID}_events"
            self.channel.queue_declare(queue=queue_name, durable=True)
            
            # Bind queue to exchange with routing patterns
            for source_server in settings.ALLOWED_SERVERS:
                routing_key = f"{source_server}.{settings.SERVER_ID}"
                self.channel.queue_bind(
                    exchange='distributed_events',
                    queue=queue_name,
                    routing_key=routing_key
                )
            
            logger.info(f"Connected to RabbitMQ at {settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def disconnect(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ")
    
    def publish_distributed_event(self, event_type: str, url: str, method: str, 
                                 inputs: Optional[Dict[str, Any]] = None, 
                                 resource_id: Optional[int] = None,
                                 operation_name: str = ""):
        """Publish event to all other servers in the distributed system"""
        self.channel.basic_publish(
            exchange='distributed_events',
            routing_key="",
            body=json.dumps(inputs),
            properties=pika.BasicProperties(
                delivery_mode=2,
                headers={
                    "operation-name": operation_name,
                    "source-server": settings.SERVER_ID,
                    "target-server": target_server
                }
            )
        )
        if not self.channel:
            if not self.connect():
                logger.error("Cannot publish event: No RabbitMQ connection")
                return False
        
        try:
            # Get target servers (all allowed servers except this one)
            target_servers = [s for s in settings.ALLOWED_SERVERS if s != settings.SERVER_ID]
            
            for target_server in target_servers:
                routing_key = f"{settings.SERVER_ID}.{target_server}"  
                
                message = {
                    "source_server": settings.SERVER_ID,
                    "target_server": target_server,
                    "event_type": event_type,  
                    "operation_name": operation_name,
                    "url": url,
                    "method": method,  
                    "inputs": inputs or {},
                    "resource_id": resource_id,
                    "timestamp": datetime.now().isoformat(),
                    "routing_key": routing_key
                }
                
                self.channel.basic_publish(
                    exchange='distributed_events',
                    routing_key=routing_key,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=2,  
                        headers={
                            "operation-name": operation_name,
                            "source-server": settings.SERVER_ID,
                            "target-server": target_server
                        }
                    )
                )
                logger.info(f"Published event to {target_server}: {event_type} - {operation_name}")
            
            return True
        except Exception as e:
            logger.error(f"Failed to publish distributed event: {e}")
            return False

# Global RabbitMQ connection instance
rabbitmq = RabbitMQConnection()


class DistributedEventProducer:
    @staticmethod
    def warehouse_created(warehouse_data: Dict[str, Any], operation_name: str):
        url = f"{settings.API_V1_STR}/warehouses/"
        inputs = {
            "name": warehouse_data.get("name"),
            "location": warehouse_data.get("location")
        }
        return rabbitmq.publish_distributed_event(
            "warehouse.created", url, "POST", inputs, None, operation_name
        )
    
    @staticmethod
    def warehouse_updated(warehouse_data: Dict[str, Any], operation_name: str):
        warehouse_id = warehouse_data.get("id")
        url = f"{settings.API_V1_STR}/warehouses/{warehouse_id}"
        inputs = {k: v for k, v in warehouse_data.items() 
                 if k in warehouse_data.get("updated_fields", [])}
        return rabbitmq.publish_distributed_event(
            "warehouse.updated", url, "PUT", inputs, warehouse_id, operation_name
        )
    
    @staticmethod
    def warehouse_deleted(warehouse_data: Dict[str, Any], operation_name: str):
        warehouse_id = warehouse_data.get("id")
        url = f"{settings.API_V1_STR}/warehouses/{warehouse_id}"
        return rabbitmq.publish_distributed_event(
            "warehouse.deleted", url, "DELETE", None, warehouse_id, operation_name
        )
    
    @staticmethod
    def shipment_created(shipment_data: Dict[str, Any], operation_name: str):
        url = f"{settings.API_V1_STR}/shipments/"
        inputs = {
            "tracking_number": shipment_data.get("tracking_number"),
            "origin": shipment_data.get("origin"),
            "destination": shipment_data.get("destination"),
            "weight": shipment_data.get("weight"),
            "warehouse_id": shipment_data.get("warehouse_id")
        }
        return rabbitmq.publish_distributed_event(
            "shipment.created", url, "POST", inputs, None, operation_name
        )
    
    @staticmethod
    def shipment_updated(shipment_data: Dict[str, Any], operation_name: str):
        shipment_id = shipment_data.get("id")
        url = f"{settings.API_V1_STR}/shipments/{shipment_id}"
        inputs = {k: v for k, v in shipment_data.items() 
                 if k in shipment_data.get("updated_fields", [])}
        return rabbitmq.publish_distributed_event(
            "shipment.updated", url, "PUT", inputs, shipment_id, operation_name
        )
    
    @staticmethod
    def shipment_deleted(shipment_data: Dict[str, Any], operation_name: str):
        shipment_id = shipment_data.get("id")
        url = f"{settings.API_V1_STR}/shipments/{shipment_id}"
        return rabbitmq.publish_distributed_event(
            "shipment.deleted", url, "DELETE", None, shipment_id, operation_name
        )


class DistributedEventConsumer:
    def __init__(self):
        self.connection = RabbitMQConnection()
        self.http_client = httpx.Client(timeout=30.0)
    
    def start_consuming(self):
        """Start consuming events for this server"""
        if not self.connection.connect():
            logger.error("Cannot start consuming: No RabbitMQ connection")
            return
        
        queue_name = f"server_{settings.SERVER_ID}_events"
        
        def callback(ch, method, properties, body):
            try:
                message = json.loads(body)
                self.process_distributed_event(message)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                
            except Exception as e:
                logger.error(f"Error processing distributed event: {e}")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
        self.connection.channel.basic_consume(queue=queue_name, on_message_callback=callback)
        logger.info(f"Started consuming distributed events for server {settings.SERVER_ID}")
        self.connection.channel.start_consuming()
    
    def process_distributed_event(self, message: Dict[str, Any]):
        """Process received distributed event"""
        source_server = message.get("source_server")
        target_server = message.get("target_server")
        event_type = message.get("event_type")
        operation_name = message.get("operation_name")
        url = message.get("url")
        method = message.get("method")
        inputs = message.get("inputs", {})
        resource_id = message.get("resource_id")
        
        logger.info(f"Processing event from {source_server}: {event_type} - {operation_name}")
        
        # Check if this server should process events from the source server
        if source_server not in settings.ALLOWED_SERVERS:
            logger.warning(f"Ignoring event from non-allowed server: {source_server}")
            return
        
        # Check if this event is targeted to this server
        if target_server != settings.SERVER_ID:
            logger.warning(f"Event not targeted to this server ({settings.SERVER_ID})")
            return
        
        # Execute the API call to replicate the action
        success = self.execute_api_call(source_server, url, method, inputs, operation_name)
        
        if success:
            logger.info(f"Successfully replicated {event_type} from {source_server}")
        else:
            logger.error(f"Failed to replicate {event_type} from {source_server}")
    
    def execute_api_call(self, source_server: str, url: str, method: str, 
                        inputs: Dict[str, Any], operation_name: str) -> bool:
        """Execute API call to replicate the action from another server"""
        try:
            # Get the base URL for this server
            base_url = settings.SERVER_ENDPOINTS.get(settings.SERVER_ID, "http://localhost:8000")
            full_url = f"{base_url}{url}"
            
            headers = {
                "operation-name": f"replicated-from-{source_server}-{operation_name}",
                "Content-Type": "application/json",
                "X-Replicated-From": source_server
            }
            
            logger.info(f"Executing {method} {full_url} with inputs: {inputs}")
            
            if method == "POST":
                response = self.http_client.post(full_url, json=inputs, headers=headers)
            elif method == "PUT":
                response = self.http_client.put(full_url, json=inputs, headers=headers)
            elif method == "DELETE":
                response = self.http_client.delete(full_url, headers=headers)
            elif method == "GET":
                response = self.http_client.get(full_url, headers=headers)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return False
            
            if response.status_code in [200, 201]:
                logger.info(f"API call successful: {response.status_code}")
                return True
            else:
                logger.error(f"API call failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error executing API call: {e}")
            return False
    
    def __del__(self):
        if hasattr(self, 'http_client'):
            self.http_client.close()


# Legacy classes for backward compatibility
EventProducer = DistributedEventProducer
EventConsumer = DistributedEventConsumer