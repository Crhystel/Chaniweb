import time
import requests
import json
import logging
import os

# Configuración
API_URL = os.getenv("API_URL", "http://backend:8000/ingest/")
# URL para verificar salud (Health Check)
HEALTH_URL = os.getenv("API_URL", "http://backend:8000/products/") 

logging.basicConfig(level=logging.INFO)

def wait_for_backend():
    """Espera activamente hasta que el Backend responda con 200 OK."""
    logging.info("Esperando a que el backend inicie...")
    max_retries = 20
    for i in range(max_retries):
        try:
            response = requests.get(HEALTH_URL.replace("/ingest/", "/products/"), timeout=5)
            if response.status_code == 200:
                logging.info("¡Backend conectado exitosamente!")
                return True
        except requests.exceptions.ConnectionError:
            pass
        except Exception as e:
            logging.warning(f"Error verificando backend: {e}")
        
        logging.info(f"Intento {i+1}/{max_retries}: Backend no listo. Reintentando en 5s...")
        time.sleep(5)
    
    logging.error("El Backend no respondió después de varios intentos.")
    return False

def send_to_backend(products):
    if not products:
        return
    try:
        response = requests.post(API_URL, json=products)
        if response.status_code in [200, 201]:
            logging.info(f"✅ Enviados {len(products)} productos a la BD.")
        else:
            logging.error(f"❌ Error del servidor: {response.text}")
    except Exception as e:
        logging.error(f"❌ Error de conexión enviando datos: {e}")

# --- SCRAPER SUPERMAXI / AKI simulado---
def scrape_favorita_group(url_ajax, supermarket_name):
    logging.info(f"Scraping {supermarket_name}...")
    
    extracted_products = []
    
    if supermarket_name == "Supermaxi":
        mock_data = [
            {"itemCode": "1859357", "description": "BONNA VIT MIEL Y CANELA", "price": 2.42},
            {"itemCode": "1427414", "description": "JOHNSON BABY JAB.ORIGINAL 3X110 G", "price": 4.50},
            {"itemCode": "1111111", "description": "ATUN REAL 180G", "price": 1.20}, 
        ]
    else: # AKI
        mock_data = [
            {"itemCode": "1767263", "description": "ARROZ SUPER EXTRA 5KG", "price": 6.50},
            {"itemCode": "9999999", "description": "ACEITE GIRA 1 LITRO", "price": 3.25},
            {"itemCode": "2222222", "description": "ATUN REAL LATA 180 GR", "price": 1.15}, 
        ]

    for item in mock_data:
        extracted_products.append({
            "external_id": item["itemCode"],
            "name": item["description"],
            "price": float(item["price"]),
            "supermarket": supermarket_name,
            "image_url": "https://via.placeholder.com/150"
        })
        
    send_to_backend(extracted_products)

# --- SCRAPER TIA ---
def scrape_tia():
    logging.info("Scraping Tía...")
    products = [
        {"external_id": "TIA-001", "name": "ARROZ TIA 5KG", "price": 5.99, "supermarket": "Tia"},
        {"external_id": "TIA-002", "name": "ATUN VAN CAMPS 180G", "price": 1.35, "supermarket": "Tia"}
    ]
    send_to_backend(products)

def run_all():
    scrape_favorita_group("https://www.supermaxi.com/wp-admin/admin-ajax.php", "Supermaxi")
    scrape_favorita_group("https://www.aki.com.ec/wp-admin/admin-ajax.php", "Aki")
    scrape_tia()

if __name__ == "__main__":
    # Primero esperamos a que el backend esté verde
    if wait_for_backend():
        run_all()
    
    # Mantiene el contenedor vivo
    while True:
        time.sleep(3600)