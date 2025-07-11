# Distributed Event-Driven Logistic System with FastAPI and RabbitMQ

This project demonstrates a **distributed event-driven architecture** using FastAPI and RabbitMQ for a logistic system. Multiple servers (A, B, C, D) can run simultaneously, and each API endpoint acts as an event that gets replicated across all other servers.

## 🌟 **Key Features**

- ✅ **Distributed Architecture**: Multiple servers sync data via RabbitMQ events
- ✅ **Event-Driven APIs**: All APIs require `operation-name` header and act as events
- ✅ **Cross-Server Replication**: Changes on one server automatically replicate to others
- ✅ **CRUD Operations**: Complete warehouse and shipment management
- ✅ **SQLite Database**: Each server has its own database that stays in sync
- ✅ **RabbitMQ Integration**: Message broker for distributed event publishing/consuming
- ✅ **Loop Prevention**: Smart middleware prevents infinite replication loops
- ✅ **URL & Input Tracking**: Events contain full API details for replication

## 🏗️ **Architecture Overview**

```
Server A (Port 8000) ←→ RabbitMQ ←→ Server B (Port 8001)
       ↕                    ↕                    ↕
   Database A          Event Queue          Database B
       ↕                    ↕                    ↕
Server D (Port 8003) ←→ RabbitMQ ←→ Server C (Port 8002)
```

### **Event Flow**
1. **API Call** → Server A receives request with `operation-name` header
2. **Database Operation** → Server A performs CRUD operation on its SQLite database
3. **Event Publishing** → Server A publishes event with URL, inputs, and operation details
4. **Event Distribution** → RabbitMQ routes event to servers B, C, D
5. **Event Consumption** → Each server receives event and replicates the API call
6. **Loop Prevention** → Replicated requests are marked to prevent re-publishing

## 📁 **Project Structure**

```
app/
├── main.py                    # FastAPI application with server identification
├── consumer.py               # Distributed RabbitMQ event consumer
├── core/
│   ├── config.py             # Server configuration with distributed settings
│   ├── rabbitmq.py           # Distributed event producer/consumer
│   └── middleware.py         # Replication detection middleware
├── db/
│   └── session.py            # Database session management
├── models/
│   ├── base.py              # SQLAlchemy base model
│   └── logistic.py          # Warehouse and Shipment models
├── schemas/
│   └── logistic.py          # Pydantic schemas for API
├── services/
│   └── logistic_service.py  # Business logic with replication awareness
└── api/
    └── api_v1/
        ├── api.py           # Main API router
        └── endpoints/
            ├── warehouses.py # Warehouse CRUD endpoints
            └── shipments.py  # Shipment CRUD endpoints

# Configuration files
.env.server_a                 # Server A configuration
.env.server_b                 # Server B configuration
start_server.py              # Multi-server startup script
```

## 🚀 **Installation & Setup**

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```
*Note: httpx is included with FastAPI for cross-server communication.*

2. **Install and start RabbitMQ**:
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

## 🎯 **Running the Distributed System**

### **Option 1: Start Individual Servers**

```bash
# Terminal 1 - Server A (Port 8000)
python start_server.py A

# Terminal 2 - Server B (Port 8001)  
python start_server.py B

# Terminal 3 - Server C (Port 8002)
python start_server.py C

# Terminal 4 - Server D (Port 8003)
python start_server.py D
```

### **Option 2: Manual Server Configuration**

```bash
# Server A
SERVER_ID=A SERVER_PORT=8000 python -m app.main

# Server B  
SERVER_ID=B SERVER_PORT=8001 python -m app.main
```

### **Start Event Consumers**

Each server needs its own consumer to receive events from other servers:

```bash
# Terminal 5 - Consumer for Server A
SERVER_ID=A python -m app.consumer

# Terminal 6 - Consumer for Server B
SERVER_ID=B python -m app.consumer

# And so on for servers C and D...
```

## 🧪 **Testing the Distributed System**

### **Test Cross-Server Replication**

1. **Create a warehouse on Server A**:
```bash
curl -X POST "http://localhost:8000/api/v1/warehouses/" \
  -H "operation-name: create-warehouse-server-a" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Main Warehouse A",
    "location": "New York, NY"
  }'
```

2. **Check if it replicated to Server B**:
```bash
curl -X GET "http://localhost:8001/api/v1/warehouses/" \
  -H "operation-name: list-warehouses-server-b"
```

3. **Update on Server C**:
```bash
curl -X PUT "http://localhost:8002/api/v1/warehouses/1" \
  -H "operation-name: update-warehouse-server-c" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Warehouse Name"
  }'
```

4. **Verify update on Server D**:
```bash
curl -X GET "http://localhost:8003/api/v1/warehouses/1" \
  -H "operation-name: get-warehouse-server-d"
```

### **Run Automated Test**

```bash
python test_system.py
```

## 📡 **Event Message Format**

Each distributed event contains complete replication information:

```json
{
  "source_server": "A",
  "target_server": "B", 
  "event_type": "warehouse.created",
  "operation_name": "create-warehouse-server-a",
  "url": "/api/v1/warehouses/",
  "method": "POST",
  "inputs": {
    "name": "Main Warehouse A",
    "location": "New York, NY"
  },
  "resource_id": null,
  "timestamp": "2024-01-01T12:00:00",
  "routing_key": "A.B"
}
```

## 🔧 **Server Configuration**

Each server can be configured via environment variables:

```bash
# Server identification
SERVER_ID=A                    # Server identifier (A, B, C, D)
SERVER_HOST=localhost          # Server host
SERVER_PORT=8000              # Server port

# Replication settings  
ALLOWED_SERVERS=["B","C","D"]  # Servers to replicate to/from
```

## 🗄️ **Database Architecture**

- Each server maintains its **own SQLite database**
- Databases stay synchronized through event replication
- Database files: `logistic_A.db`, `logistic_B.db`, etc.
- Tables: `warehouses`, `shipments`

## 🐰 **RabbitMQ Configuration**

- **Exchange**: `distributed_events` (topic exchange)
- **Queues**: 
  - `server_A_events` (receives events for Server A)
  - `server_B_events` (receives events for Server B)
  - `server_C_events` (receives events for Server C)
  - `server_D_events` (receives events for Server D)
- **Routing Keys**: `{source}.{target}` (e.g., `A.B`, `B.A`)

## 🔄 **Replication Logic**

1. **Original Request**: Server A receives API call
2. **Local Processing**: Server A updates its database
3. **Event Publishing**: Server A publishes event to servers B, C, D
4. **Event Consumption**: Servers B, C, D receive and process event
5. **API Replication**: Each server calls its own API with `X-Replicated-From` header
6. **Loop Prevention**: Replicated requests don't trigger new events

## 🛡️ **Loop Prevention**

- **Middleware Detection**: `ReplicationMiddleware` detects replicated requests
- **Header Marking**: Replicated requests include `X-Replicated-From` header
- **Event Suppression**: Services skip event publishing for replicated requests
- **Source Tracking**: Each request tracks its originating server

## 🎮 **API Endpoints**

All endpoints require `operation-name` header and support cross-server replication:

### **Warehouses**
- `POST /api/v1/warehouses/` - Create warehouse
- `GET /api/v1/warehouses/` - List warehouses  
- `GET /api/v1/warehouses/{id}` - Get warehouse
- `PUT /api/v1/warehouses/{id}` - Update warehouse
- `DELETE /api/v1/warehouses/{id}` - Delete warehouse

### **Shipments**
- `POST /api/v1/shipments/` - Create shipment
- `GET /api/v1/shipments/` - List shipments
- `GET /api/v1/shipments/{id}` - Get shipment
- `GET /api/v1/shipments/tracking/{number}` - Track shipment
- `PUT /api/v1/shipments/{id}` - Update shipment
- `DELETE /api/v1/shipments/{id}` - Delete shipment

## 📊 **Monitoring & Logs**

Each server provides detailed logging:
- **Event Publishing**: When events are sent to other servers
- **Event Consumption**: When events are received and processed
- **Replication Detection**: When replicated requests are identified
- **API Replication**: When cross-server API calls are made

## 🔍 **API Documentation**

Each server provides its own Swagger documentation:
- Server A: `http://localhost:8000/docs`
- Server B: `http://localhost:8001/docs`
- Server C: `http://localhost:8002/docs`
- Server D: `http://localhost:8003/docs`

## 🚨 **Error Handling**

- **RabbitMQ Unavailable**: Servers continue operating without replication
- **Target Server Down**: Events are queued until server comes back online
- **Database Conflicts**: Each server maintains its own database state
- **Network Issues**: Automatic retry mechanisms for cross-server calls

## 🎯 **Use Cases**

This distributed architecture is perfect for:
- **Multi-region deployments** with data synchronization
- **High availability systems** with automatic failover
- **Event sourcing patterns** with complete audit trails
- **Microservices communication** via event-driven patterns
- **Real-time data replication** across distributed systems

## 🔮 **Future Enhancements**

- **Conflict Resolution**: Handle concurrent updates across servers
- **Event Ordering**: Ensure events are processed in correct order
- **Partial Replication**: Configure which events to replicate
- **Health Monitoring**: Dashboard for distributed system health
- **Load Balancing**: Distribute requests across available servers