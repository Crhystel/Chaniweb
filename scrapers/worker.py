import time
import requests
import logging
import os

# Configuración
API_URL = os.getenv("API_URL", "http://backend:8000/ingest/")
HEALTH_URL = os.getenv("API_URL", "http://backend:8000/products/").replace("/ingest/", "/products/")

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def wait_for_backend():
    logging.info("Esperando al backend...")
    for i in range(30):
        try:
            if requests.get(HEALTH_URL, timeout=5).status_code == 200:
                return True
        except:
            pass
        time.sleep(2)
    return False

def send_to_backend(products):
    if not products: return
    try:
        response = requests.post(API_URL, json=products)
        if response.status_code in [200, 201]:
            logging.info(f"📤 Inyectados {len(products)} productos de {products[0]['supermarket']}")
        else:
            logging.error(f"❌ Error {response.status_code}: {response.text}")
    except Exception as e:
        logging.error(f"❌ Error de conexión: {e}")

# --- DATA SEEDING ---

def get_micomisariato_data():
    return [
        # Alimentos Básicos
        {"external_id": "MC-01", "supermarket": "Mi Comisariato", "name": "Atún Real en Aceite de Girasol 180g", "price": 1.35, "image_url": "https://tienda.alimentosreal.com/wp-content/uploads/2021/03/Lomitos-girasol-180g.jpg"},
        {"external_id": "MC-02", "supermarket": "Mi Comisariato", "name": "Arroz Flor Super Arroz 5 kg", "price": 4.50, "image_url": "https://www.corporacionfavorita.com/wp-content/uploads/2020/05/Flor-Super-Arroz.png"},
        {"external_id": "MC-03", "supermarket": "Mi Comisariato", "name": "Aceite La Favorita 1 Litro", "price": 2.85, "image_url": "https://www.corporacionfavorita.com/wp-content/uploads/2020/05/Aceite-La-Favorita-Original.png"},
        {"external_id": "MC-04", "supermarket": "Mi Comisariato", "name": "Leche Entera Vita 1L", "price": 0.95, "image_url": "https://vitaleche.com/wp-content/uploads/2021/06/leche-entera-1-litro.png"},
        {"external_id": "MC-05", "supermarket": "Mi Comisariato", "name": "Cubeta Huevos 30 Unidades", "price": 3.99, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170305886_M.jpg"},
        {"external_id": "MC-06", "supermarket": "Mi Comisariato", "name": "Azúcar Blanca San Carlos 2kg", "price": 1.95, "image_url": "https://sancarlos.com.ec/wp-content/uploads/2020/09/azucar-blanca-2kg.png"},
        {"external_id": "MC-07", "supermarket": "Mi Comisariato", "name": "Fideos Tallarín Sumesa 400g", "price": 0.85, "image_url": "https://sumesa.com.ec/wp-content/uploads/2021/06/TALLARIN.png"},
        
        # Carnes
        {"external_id": "MC-08", "supermarket": "Mi Comisariato", "name": "Pollo Entero Mr. Pollo por Kg", "price": 2.60, "image_url": "https://www.corporacionfavorita.com/wp-content/uploads/2020/05/Mr-Pollo.png"},
        {"external_id": "MC-09", "supermarket": "Mi Comisariato", "name": "Carne Molida Especial Kg", "price": 5.50, "image_url": "https://cdn.pixabay.com/photo/2016/01/22/02/13/meat-1155132_1280.jpg"},
        
        # Limpieza y Aseo
        {"external_id": "MC-10", "supermarket": "Mi Comisariato", "name": "Crema Lavavajillas Lava 900g", "price": 1.60, "image_url": "https://jaboneriavail.com.ec/wp-content/uploads/2020/05/LAVA-900.png"},
        {"external_id": "MC-11", "supermarket": "Mi Comisariato", "name": "Detergente Deja Floral 2kg", "price": 4.20, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170462002_M.jpg"},
        {"external_id": "MC-12", "supermarket": "Mi Comisariato", "name": "Crema dental Colgate Max Fresh 75ml", "price": 2.99, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170364860_M.jpg"},
        {"external_id": "MC-13", "supermarket": "Mi Comisariato", "name": "Papel Higiénico Familia 12 Rollos", "price": 6.50, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170198647_M.jpg"},
    ]

def get_aki_data():
    return [
        {"external_id": "AKI-01", "supermarket": "Akí", "name": "Atún Real en Aceite de Girasol 180g", "price": 1.28, "image_url": "https://tienda.alimentosreal.com/wp-content/uploads/2021/03/Lomitos-girasol-180g.jpg"},
        {"external_id": "AKI-02", "supermarket": "Akí", "name": "Arroz Flor Super Arroz 5 kg", "price": 4.35, "image_url": "https://www.corporacionfavorita.com/wp-content/uploads/2020/05/Flor-Super-Arroz.png"},
        {"external_id": "AKI-03", "supermarket": "Akí", "name": "Aceite La Favorita 1 Litro", "price": 2.75, "image_url": "https://www.corporacionfavorita.com/wp-content/uploads/2020/05/Aceite-La-Favorita-Original.png"},
        {"external_id": "AKI-04", "supermarket": "Akí", "name": "Leche Entera Vita 1L", "price": 0.89, "image_url": "https://vitaleche.com/wp-content/uploads/2021/06/leche-entera-1-litro.png"},
        {"external_id": "AKI-05", "supermarket": "Akí", "name": "Cubeta Huevos 30 Unidades", "price": 3.85, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170305886_M.jpg"},
        {"external_id": "AKI-06", "supermarket": "Akí", "name": "Azúcar Blanca San Carlos 2kg", "price": 1.85, "image_url": "https://sancarlos.com.ec/wp-content/uploads/2020/09/azucar-blanca-2kg.png"},
        {"external_id": "AKI-07", "supermarket": "Akí", "name": "Fideos Tallarín Sumesa 400g", "price": 0.80, "image_url": "https://sumesa.com.ec/wp-content/uploads/2021/06/TALLARIN.png"},
        {"external_id": "AKI-08", "supermarket": "Akí", "name": "Pollo Entero Mr. Pollo por Kg", "price": 2.45, "image_url": "https://www.corporacionfavorita.com/wp-content/uploads/2020/05/Mr-Pollo.png"},
        {"external_id": "AKI-09", "supermarket": "Akí", "name": "Carne Molida Especial Kg", "price": 5.25, "image_url": "https://cdn.pixabay.com/photo/2016/01/22/02/13/meat-1155132_1280.jpg"},
        {"external_id": "AKI-10", "supermarket": "Akí", "name": "Crema Lavavajillas Lava 900g", "price": 1.50, "image_url": "https://jaboneriavail.com.ec/wp-content/uploads/2020/05/LAVA-900.png"},
        {"external_id": "AKI-11", "supermarket": "Akí", "name": "Detergente Deja Floral 2kg", "price": 3.99, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170462002_M.jpg"},
        {"external_id": "AKI-12", "supermarket": "Akí", "name": "Crema dental Colgate Max Fresh 75ml", "price": 2.85, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170364860_M.jpg"},
        {"external_id": "AKI-13", "supermarket": "Akí", "name": "Papel Higiénico Familia 12 Rollos", "price": 6.20, "image_url": "https://www.supermercadosantamaria.com/documents/10180/10504/170198647_M.jpg"},
    ]

def run_scrapers():
    logging.info("🚀 Ejecutando Scrapers de Sprint 3 (Mi Comisariato & Akí)...")
    send_to_backend(get_micomisariato_data())
    send_to_backend(get_aki_data())

if __name__ == "__main__":
    if wait_for_backend():
        while True:
            run_scrapers()
            logging.info("Datos actualizados. Esperando 1 hora...")
            time.sleep(3600)