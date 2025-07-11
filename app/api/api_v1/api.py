from fastapi import APIRouter, Header
from app.api.api_v1.endpoints import warehouses, shipments

api_router = APIRouter()

# Include routers
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(shipments.router, prefix="/shipments", tags=["shipments"])

# Health check route with operation-name header
@api_router.get("/ping", tags=["health"])
def ping(operation_name: str = Header(..., alias="operation-name")):
    return {"msg": "pong", "operation": operation_name}
