import time
import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError
from typing import List
from . import models, database

# Configuración de Logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- LÓGICA DE REINTENTO (WAIT FOR DB) ---
def wait_for_db():
    max_retries = 30
    for i in range(max_retries):
        try:
            models.Base.metadata.create_all(bind=database.engine)
            logger.info("✅ Base de datos conectada exitosamente.")
            return
        except OperationalError:
            logger.warning(f"⏳ Base de datos no lista. Reintentando ({i+1}/{max_retries})...")
            time.sleep(2)
    logger.error("❌ No se pudo conectar a la BD después de varios intentos.")

wait_for_db()

app = FastAPI(title="ChaniWeb Core API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ingest/", status_code=201)
def ingest_products(products: List[models.ProductCreate], db: Session = Depends(database.get_db)):
    from .logic import normalize_and_save
    count = 0
    for p in products:
        normalize_and_save(db, p)
        count += 1
    return {"message": f"{count} productos procesados"}

@app.get("/products/", response_model=List[models.ProductResponse])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db)):
    return db.query(models.ProductDB).offset(skip).limit(limit).all()