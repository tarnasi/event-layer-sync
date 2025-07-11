from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class WarehouseBase(BaseModel):
    name: str
    location: str


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None


class Warehouse(WarehouseBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ShipmentBase(BaseModel):
    tracking_number: str
    origin: str
    destination: str
    weight: float
    warehouse_id: int


class ShipmentCreate(ShipmentBase):
    pass


class ShipmentUpdate(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    weight: Optional[float] = None
    status: Optional[str] = None
    warehouse_id: Optional[int] = None


class Shipment(ShipmentBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ShipmentWithWarehouse(Shipment):
    warehouse: Warehouse


class WarehouseWithShipments(Warehouse):
    shipments: List[Shipment] = []