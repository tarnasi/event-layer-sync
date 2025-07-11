from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    shipments = relationship("Shipment", back_populates="warehouse")


class Shipment(Base):
    __tablename__ = "shipments"
    
    id = Column(Integer, primary_key=True, index=True)
    tracking_number = Column(String, unique=True, nullable=False, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    status = Column(String, default="pending")  # pending, in_transit, delivered
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    warehouse = relationship("Warehouse", back_populates="shipments")