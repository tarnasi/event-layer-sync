# Event-Driven Logistic System with FastAPI and RabbitMQ

This project demonstrates an event-driven architecture using FastAPI and RabbitMQ for a simple logistic system. Every API endpoint acts as an event and requires an `operation-name` header.

## Features

- ✅ **Event-Driven APIs**: All APIs require `operation-name` header and act as events
- ✅ **CRUD Operations**: Complete warehouse and shipment management
- ✅ **SQLite Database**: Persistent storage with SQLAlchemy
- ✅ **RabbitMQ Integration**: Message broker for event publishing/consuming
- ✅ **Producer/Consumer System**: Separate event producer and consumer components

## Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── consumer.py            # RabbitMQ event consumer
├── core/
│   ├── config.py          # Application configuration
│   └── rabbitmq.py        # RabbitMQ connection and event handling
├── db/
│   └── session.py         # Database session management
├── models/
│   ├── base.py           # SQLAlchemy base model
│   └── logistic.py       # Warehouse and Shipment models
├── schemas/
│   └── logistic.py       # Pydantic schemas for API
├── services/
│   └── logistic_service.py # Business logic layer
└── api/
    └── api_v1/
        ├── api.py         # Main API router
        └── endpoints/
            ├── warehouses.py # Warehouse CRUD endpoints
            └── shipments.py  # Shipment CRUD endpoints
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install and start RabbitMQ (optional - system works without it):
```bash
# On Windows with Chocolatey
choco install rabbitmq

# On macOS with Homebrew
brew install rabbitmq

# On Ubuntu/Debian
sudo apt-get install rabbitmq-server

# Start RabbitMQ
rabbitmq-server
```

## Usage

### 1. Start the FastAPI Server

```bash
python -m app.main
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- OpenAPI Schema: `http://localhost:8000/api/v1/openapi.json`

### 2. Start Event Consumers (Optional)

Open separate terminals and run:

```bash
# Consumer for warehouse events
python -m app.consumer warehouse_events

# Consumer for shipment events  
python -m app.consumer shipment_events
```

### 3. Test the System

Run the test script to see the system in action:

```bash
python test_system.py
```

## API Usage

All API endpoints require the `operation-name` header:

### Create Warehouse
```bash
curl -X POST "http://localhost:8000/api/v1/warehouses/" \
  -H "operation-name: create-warehouse-001" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Warehouse",
    "location": "New York, NY"
  }'
```

### Create Shipment
```bash
curl -X POST "http://localhost:8000/api/v1/shipments/" \
  -H "operation-name: create-shipment-001" \
  -H "Content-Type: application/json" \
  -d '{
    "tracking_number": "TRK001",
    "origin": "New York, NY", 
    "destination": "Los Angeles, CA",
    "weight": 25.5,
    "warehouse_id": 1
  }'
```

### Update Shipment Status
```bash
curl -X PUT "http://localhost:8000/api/v1/shipments/1" \
  -H "operation-name: update-shipment-status" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_transit"
  }'
```

### Get All Warehouses
```bash
curl -X GET "http://localhost:8000/api/v1/warehouses/" \
  -H "operation-name: list-warehouses"
```

## Event System

### Event Flow
1. **API Call** → Requires `operation-name` header
2. **Database Operation** → CRUD operation on SQLite
3. **Event Publishing** → Publishes event to RabbitMQ with operation name
4. **Event Consumption** → Consumer processes the event

### Event Types
- `warehouse.created` - When a warehouse is created
- `warehouse.updated` - When a warehouse is updated  
- `warehouse.deleted` - When a warehouse is deleted
- `shipment.created` - When a shipment is created
- `shipment.updated` - When a shipment is updated
- `shipment.deleted` - When a shipment is deleted

### Event Message Format
```json
{
  "operation_name": "create-warehouse-001",
  "event_data": {
    "id": 1,
    "name": "Main Warehouse",
    "location": "New York, NY",
    "created_at": "2024-01-01T12:00:00"
  },
  "timestamp": "2024-01-01T12:00:00",
  "routing_key": "warehouse.created"
}
```

## Database

The system uses SQLite with the following tables:
- **warehouses**: Store warehouse information
- **shipments**: Store shipment details with warehouse relationships

Database file: `logistic.db` (created automatically)

## RabbitMQ Configuration

- **Exchange**: `logistic_events` (topic exchange)
- **Queues**: 
  - `warehouse_events` (bound to `warehouse.*`)
  - `shipment_events` (bound to `shipment.*`)

## Development

The system is designed to work with or without RabbitMQ:
- **With RabbitMQ**: Full event-driven architecture with message publishing/consuming
- **Without RabbitMQ**: APIs work normally, events are logged but not published

## Testing

Use the provided test script to verify all functionality:
```bash
python test_system.py
```

This will test all CRUD operations and demonstrate the event system in action.