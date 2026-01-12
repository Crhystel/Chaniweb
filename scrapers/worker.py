import time
import requests
import json
import logging
import os

API_URL = os.getenv("API_URL", "http://backend:8000/ingest/")
logging.basicConfig(level=logging.INFO)

def send_to_backend(products):
    if not products:
        return
    try:
        response = requests.post(API_URL, json=products)
        logging.info(f"Enviados {len(products)} productos. Status: {response.status_code}")
    except Exception as e:
        logging.error(f"Error enviando al backend: {e}")

# --- SCRAPER SUPERMAXI / AKI (Estrategia AJAX) ---
def scrape_favorita_group(url_ajax, supermarket_name):
    logging.info(f"Iniciando scraping de {supermarket_name}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    
    # payload estándar para búsqueda/filtro en estos sitios WP
    
    extracted_products = []
    
    # INTENTO 1: Petición Real 
    try:
        data = {
            'action': 'get_products_by_category', # Nombre común deducido
            'cat_id': 'all' 
        }
        # r = requests.post(url_ajax, data=data, headers=headers)
        # if r.status_code == 200:
        #    parse_json_response(r.json())
        pass 
    except:
        pass
    
    if supermarket_name == "Supermaxi":
        # Datos simulados 
        mock_data = [
            {"itemCode": "1859357", "description": "BONNA VIT MIEL Y CANELA", "price": 2.42},
            {"itemCode": "1427414", "description": "JOHNSON BABY JAB.ORIGINAL 3X110 G", "price": 4.50},
        ]
    else: # AKI
        mock_data = [
            {"itemCode": "1767263", "description": "ARROZ SUPER EXTRA 5KG", "price": 6.50},
            {"itemCode": "9999999", "description": "ACEITE GIRA 1 LITRO", "price": 3.25},
        ]

    for item in mock_data:
        extracted_products.append({
            "external_id": item["itemCode"],
            "name": item["description"],
            "price": float(item["price"]),
            "supermarket": supermarket_name,
            "image_url": "https://via.placeholder.com/150" # Placeholder
        })
        
    send_to_backend(extracted_products)

# --- SCRAPER TIA (Estrategia HTML/API) ---
def scrape_tia():
    logging.info("Iniciando scraping de Tía...")
    # Tía usa VTEX usualmente
    products = [
        {"external_id": "TIA-001", "name": "ARROZ TIA 5KG", "price": 5.99, "supermarket": "Tia"},
        {"external_id": "TIA-002", "name": "ATUN REAL 180G", "price": 1.15, "supermarket": "Tia"}
    ]
    send_to_backend(products)

def run_all():
    scrape_favorita_group("https://www.supermaxi.com/wp-admin/admin-ajax.php", "Supermaxi")
    scrape_favorita_group("https://www.aki.com.ec/wp-admin/admin-ajax.php", "Aki")
    scrape_tia()

if __name__ == "__main__":
    # Ejecutar inmediatamente al levantar (Sprint 1 requirement)
    logging.info("Worker iniciado. Ejecutando primera carga...")
    time.sleep(10) # Esperar a que backend y DB estén listos
    run_all()
    
    # Mantener vivo el contenedor
    while True:
        time.sleep(3600)