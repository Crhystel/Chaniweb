from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, database

# Crear tablas al iniciar
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="ChaniWeb Core API")

# Configurar CORS para permitir peticiones desde el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción cambiar por dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest/", status_code=201)
def ingest_products(products: List[models.ProductCreate], db: Session = Depends(database.get_db)):
    """Endpoint interno para que los Scrapers guarden datos."""
    from .logic import normalize_and_save # Importación diferida
    count = 0
    for p in products:
        normalize_and_save(db, p)
        count += 1
    return {"message": f"{count} productos procesados correctamente"}

@app.get("/products/", response_model=List[models.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    """Endpoint para el Frontend (HU-03)."""
    return db.query(models.ProductDB).offset(skip).limit(limit).all()