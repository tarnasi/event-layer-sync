from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.schemas.logistic import Warehouse, WarehouseCreate, WarehouseUpdate
from app.services.logistic_service import WarehouseService

router = APIRouter()


@router.post("/", response_model=Warehouse)
def create_warehouse(
    warehouse: WarehouseCreate,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Create a new warehouse - This API acts as an event with operation-name header"""
    return WarehouseService.create_warehouse(db, warehouse, operation_name)


@router.get("/", response_model=List[Warehouse])
def read_warehouses(
    skip: int = 0,
    limit: int = 100,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Get all warehouses - This API acts as an event with operation-name header"""
    return WarehouseService.get_warehouses(db, skip=skip, limit=limit)


@router.get("/{warehouse_id}", response_model=Warehouse)
def read_warehouse(
    warehouse_id: int,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Get a specific warehouse - This API acts as an event with operation-name header"""
    warehouse = WarehouseService.get_warehouse(db, warehouse_id)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.put("/{warehouse_id}", response_model=Warehouse)
def update_warehouse(
    warehouse_id: int,
    warehouse_update: WarehouseUpdate,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Update a warehouse - This API acts as an event with operation-name header"""
    warehouse = WarehouseService.update_warehouse(db, warehouse_id, warehouse_update, operation_name)
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return warehouse


@router.delete("/{warehouse_id}")
def delete_warehouse(
    warehouse_id: int,
    operation_name: str = Header(..., alias="operation-name"),
    db: Session = Depends(get_db)
):
    """Delete a warehouse - This API acts as an event with operation-name header"""
    success = WarehouseService.delete_warehouse(db, warehouse_id, operation_name)
    if not success:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return {"message": "Warehouse deleted successfully"}