import time
import requests
import logging
import os
import random

# Configuración del entorno 
API_URL = os.getenv("API_URL", "http://backend:8000/ingest/")
HEALTH_URL = os.getenv("API_URL", "http://backend:8000/products/").replace("/ingest/", "/products/")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def wait_for_backend():
    """Espera activamente hasta que el Backend responda (Health Check)."""
    logging.info(f"Conectando a {HEALTH_URL}...")
    for i in range(30):
        try:
            response = requests.get(HEALTH_URL, timeout=5)
            if response.status_code == 200:
                logging.info("✅ Backend operativo.")
                return True
        except Exception:
            pass
        logging.info(f"⏳ Esperando backend ({i+1}/30)...")
        time.sleep(5)
    return False

def send_to_backend(products):
    if not products:
        return
    try:
        # Enviamos al API Gateway / Backend
        response = requests.post(API_URL, json=products)
        if response.status_code in [200, 201]:
            logging.info(f"📤 Enviados {len(products)} productos correctamente.")
        else:
            logging.error(f"❌ Error servidor: {response.text}")
    except Exception as e:
        logging.error(f"❌ Fallo de conexión: {e}")

# --- SCRAPERS ESPECÍFICOS (Simulación de Ingesta Estable) ---

def get_supermaxi_data():
    """Simula extracción de Supermaxi (Categoría: Despensa)"""
    return [
        {"external_id": "SMX-001", "name": "ARROZ SUPERMAXI 2KG", "price": 3.20, "image_url": "https://imgs.supermaxi.com/smx001.jpg"},
        {"external_id": "SMX-002", "name": "ATUN REAL EN ACEITE 180G", "price": 1.25, "image_url": "https://imgs.supermaxi.com/smx002.jpg"},
        {"external_id": "SMX-003", "name": "ACEITE GIRASOL 1 LITRO", "price": 2.99, "image_url": "https://imgs.supermaxi.com/smx003.jpg"},
        {"external_id": "SMX-004", "name": "LECHE VITA ENTERA 1L", "price": 0.95, "image_url": "https://imgs.supermaxi.com/smx004.jpg"},
        {"external_id": "SMX-005", "name": "HUEVOS INDAVES ROJOS 12U", "price": 2.15, "image_url": "https://imgs.supermaxi.com/smx005.jpg"},
    ]

def get_tia_data():
    """Simula extracción de Tía (Categoría: Canasta Básica)"""
    return [
        {"external_id": "TIA-001", "name": "ARROZ TIA 2000 G", "price": 3.10, "image_url": "https://imgs.tia.com.ec/tia001.jpg"}, # Más barato que SMX
        {"external_id": "TIA-002", "name": "LATA ATUN REAL 180 GR ACEITE", "price": 1.29, "image_url": "https://imgs.tia.com.ec/tia002.jpg"}, # Más caro
        {"external_id": "TIA-003", "name": "ACEITE LA FAVORITA 1L", "price": 3.05, "image_url": "https://imgs.tia.com.ec/tia003.jpg"},
        {"external_id": "TIA-004", "name": "LECHE PARAMONGA 1 LITRO", "price": 0.90, "image_url": "https://imgs.tia.com.ec/tia004.jpg"},
        {"external_id": "TIA-005", "name": "CUBETA HUEVOS 12 UNIDADES", "price": 2.10, "image_url": "https://imgs.tia.com.ec/tia005.jpg"},
    ]

def run_scrapers():
    logging.info("🚀 Iniciando ciclo de Scraping: Supermaxi & Tía")
    
    # 1. Procesar Supermaxi
    smx_products = get_supermaxi_data()
    for p in smx_products: p['supermarket'] = 'Supermaxi'
    send_to_backend(smx_products)

    # 2. Procesar Tía
    tia_products = get_tia_data()
    for p in tia_products: p['supermarket'] = 'Tia'
    send_to_backend(tia_products)

if __name__ == "__main__":
    if wait_for_backend():
        # Ciclo infinito para mantener el pod vivo 
        while True:
            run_scrapers()
            logging.info("💤 Durmiendo 1 hora hasta la próxima actualización...")
            time.sleep(3600)