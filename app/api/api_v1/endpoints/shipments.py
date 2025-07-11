from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.logistic import Shipment, ShipmentCreate, ShipmentUpdate
from app.services.logistic_service import ShipmentService

router = APIRouter()


@router.post("/", response_model=Shipment)
def create_shipment(
    shipment: ShipmentCreate,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Create a new shipment - This API acts as an event with operation-name header"""
    return ShipmentService.create_shipment(db, shipment, operation_name)


@router.get("/", response_model=List[Shipment])
def read_shipments(
    skip: int = 0,
    limit: int = 100,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Get all shipments - This API acts as an event with operation-name header"""
    return ShipmentService.get_shipments(db, skip=skip, limit=limit)


@router.get("/{shipment_id}", response_model=Shipment)
def read_shipment(
    shipment_id: int,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Get a specific shipment - This API acts as an event with operation-name header"""
    shipment = ShipmentService.get_shipment(db, shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.get("/tracking/{tracking_number}", response_model=Shipment)
def read_shipment_by_tracking(
    tracking_number: str,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Get shipment by tracking number - This API acts as an event with operation-name header"""
    shipment = ShipmentService.get_shipment_by_tracking(db, tracking_number)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.put("/{shipment_id}", response_model=Shipment)
def update_shipment(
    shipment_id: int,
    shipment_update: ShipmentUpdate,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Update a shipment - This API acts as an event with operation-name header"""
    shipment = ShipmentService.update_shipment(db, shipment_id, shipment_update, operation_name)
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipment


@router.delete("/{shipment_id}")
def delete_shipment(
    shipment_id: int,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Delete a shipment - This API acts as an event with operation-name header"""
    success = ShipmentService.delete_shipment(db, shipment_id, operation_name)
    if not success:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return {"message": "Shipment deleted successfully"}