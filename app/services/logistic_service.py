from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.logistic import Warehouse, Shipment
from app.schemas.logistic import (
    WarehouseCreate, WarehouseUpdate, 
    ShipmentCreate, ShipmentUpdate
)
from app.core.rabbitmq import EventProducer


class WarehouseService:
    @staticmethod
    def create_warehouse(db: Session, warehouse: WarehouseCreate, operation_name: str) -> Warehouse:
        db_warehouse = Warehouse(**warehouse.dict())
        db.add(db_warehouse)
        db.commit()
        db.refresh(db_warehouse)
        
        # Publish event
        EventProducer.warehouse_created(
            {
                "id": db_warehouse.id,
                "name": db_warehouse.name,
                "location": db_warehouse.location,
                "created_at": db_warehouse.created_at.isoformat()
            },
            operation_name
        )
        
        return db_warehouse
    
    @staticmethod
    def get_warehouse(db: Session, warehouse_id: int) -> Optional[Warehouse]:
        return db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    
    @staticmethod
    def get_warehouses(db: Session, skip: int = 0, limit: int = 100) -> List[Warehouse]:
        return db.query(Warehouse).offset(skip).limit(limit).all()
    
    @staticmethod
    def update_warehouse(db: Session, warehouse_id: int, warehouse_update: WarehouseUpdate, operation_name: str) -> Optional[Warehouse]:
        db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not db_warehouse:
            return None
        
        update_data = warehouse_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_warehouse, field, value)
        
        db.commit()
        db.refresh(db_warehouse)
        
        # Publish event
        EventProducer.warehouse_updated(
            {
                "id": db_warehouse.id,
                "name": db_warehouse.name,
                "location": db_warehouse.location,
                "updated_fields": list(update_data.keys())
            },
            operation_name
        )
        
        return db_warehouse
    
    @staticmethod
    def delete_warehouse(db: Session, warehouse_id: int, operation_name: str) -> bool:
        db_warehouse = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not db_warehouse:
            return False
        
        warehouse_data = {
            "id": db_warehouse.id,
            "name": db_warehouse.name,
            "location": db_warehouse.location
        }
        
        db.delete(db_warehouse)
        db.commit()
        
        # Publish event
        EventProducer.warehouse_deleted(warehouse_data, operation_name)
        
        return True


class ShipmentService:
    @staticmethod
    def create_shipment(db: Session, shipment: ShipmentCreate, operation_name: str) -> Shipment:
        db_shipment = Shipment(**shipment.dict())
        db.add(db_shipment)
        db.commit()
        db.refresh(db_shipment)
        
        # Publish event
        EventProducer.shipment_created(
            {
                "id": db_shipment.id,
                "tracking_number": db_shipment.tracking_number,
                "origin": db_shipment.origin,
                "destination": db_shipment.destination,
                "weight": db_shipment.weight,
                "status": db_shipment.status,
                "warehouse_id": db_shipment.warehouse_id,
                "created_at": db_shipment.created_at.isoformat()
            },
            operation_name
        )
        
        return db_shipment
    
    @staticmethod
    def get_shipment(db: Session, shipment_id: int) -> Optional[Shipment]:
        return db.query(Shipment).filter(Shipment.id == shipment_id).first()
    
    @staticmethod
    def get_shipments(db: Session, skip: int = 0, limit: int = 100) -> List[Shipment]:
        return db.query(Shipment).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_shipment_by_tracking(db: Session, tracking_number: str) -> Optional[Shipment]:
        return db.query(Shipment).filter(Shipment.tracking_number == tracking_number).first()
    
    @staticmethod
    def update_shipment(db: Session, shipment_id: int, shipment_update: ShipmentUpdate, operation_name: str) -> Optional[Shipment]:
        db_shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not db_shipment:
            return None
        
        update_data = shipment_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_shipment, field, value)
        
        db.commit()
        db.refresh(db_shipment)
        
        # Publish event
        EventProducer.shipment_updated(
            {
                "id": db_shipment.id,
                "tracking_number": db_shipment.tracking_number,
                "origin": db_shipment.origin,
                "destination": db_shipment.destination,
                "weight": db_shipment.weight,
                "status": db_shipment.status,
                "warehouse_id": db_shipment.warehouse_id,
                "updated_fields": list(update_data.keys())
            },
            operation_name
        )
        
        return db_shipment
    
    @staticmethod
    def delete_shipment(db: Session, shipment_id: int, operation_name: str) -> bool:
        db_shipment = db.query(Shipment).filter(Shipment.id == shipment_id).first()
        if not db_shipment:
            return False
        
        shipment_data = {
            "id": db_shipment.id,
            "tracking_number": db_shipment.tracking_number,
            "origin": db_shipment.origin,
            "destination": db_shipment.destination,
            "weight": db_shipment.weight,
            "status": db_shipment.status,
            "warehouse_id": db_shipment.warehouse_id
        }
        
        db.delete(db_shipment)
        db.commit()
        
        # Publish event
        EventProducer.shipment_deleted(shipment_data, operation_name)
        
        return True