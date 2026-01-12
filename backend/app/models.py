from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from .database import Base
from pydantic import BaseModel
from typing import Optional

# --- Modelo de Base de Datos (SQLAlchemy) ---
class ProductDB(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String, index=True) # ID original del supermercado
    name = Column(String, index=True)
    supermarket = Column(String) 
    price = Column(Float)
    image_url = Column(String, nullable=True)
    
    # Campos para el Algoritmo de Comparación (T-05)
    normalized_name = Column(String) 
    unit = Column(String)            
    quantity = Column(Float)         
    price_per_unit = Column(Float)   
    
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

# --- Schemas de Validación (Pydantic) ---
class ProductBase(BaseModel):
    name: str
    supermarket: str
    price: float
    image_url: Optional[str] = None
    external_id: str

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int
    normalized_name: Optional[str]
    quantity: Optional[float]
    unit: Optional[str]
    price_per_unit: Optional[float]

    class Config:
        orm_mode = True