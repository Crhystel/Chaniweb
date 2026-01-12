import time
import requests
import logging
import os
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN ---
API_URL = os.getenv("API_URL", "http://backend:8000/ingest/")
HEALTH_URL = os.getenv("API_URL", "http://backend:8000/products/").replace("/ingest/", "/products/")

URL_CATEGORIAS = "https://app.frecuento.com/categories/?image_quality=100"
URL_PRODUCTOS = "https://app.frecuento.com/products/"

# Filtros
PALABRAS_CLAVE_COMIDA = ["despensa", "alimentos", "arroz", "aceite", "atun", "leche", "carnes", "pollo", "bebidas", "huevos", "queso", "frutas", "verduras"]
PALABRAS_EXCLUIDAS = ["mascotas", "hogar", "electro", "escolar"]

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def wait_for_backend():
    logging.info(f"🔍 Buscando backend en: {HEALTH_URL}")
    for i in range(10):
        try:
            r = requests.get(HEALTH_URL, timeout=5)
            if r.status_code == 200:
                logging.info("✅ Backend operativo.")
                return True
        except:
            pass
        time.sleep(3)
    return False

def send_to_backend(products):
    if not products: return
    try:
        r = requests.post(API_URL, json=products)
        if r.status_code in [200, 201]:
            logging.info(f"📤 Enviados {len(products)} productos.")
        else:
            logging.error(f"❌ Error Backend ({r.status_code}): {r.text}")
    except Exception as e:
        logging.error(f"❌ Error enviando: {e}")

def obtener_headers_auth():
    logging.info("🍪 Abriendo navegador para obtener sesión...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
            page = context.new_page()
            page.goto("https://www.frecuento.com/", timeout=60000)
            time.sleep(5)
            cookies = context.cookies()
            cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
            browser.close()
            return {
                "authority": "app.frecuento.com",
                "accept": "application/json, text/plain, */*",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "cookie": cookie_str,
                "origin": "https://www.frecuento.com",
                "referer": "https://www.frecuento.com/"
            }
    except Exception as e:
        logging.error(f"❌ Error Playwright: {e}")
        return None

def es_comida(nombre):
    n = nombre.lower()
    if any(x in n for x in PALABRAS_EXCLUIDAS): return False
    return any(x in n for x in PALABRAS_CLAVE_COMIDA)

def run_scraper():
    headers = obtener_headers_auth()
    if not headers: return

    # 1. Categorías
    logging.info("📂 Bajando categorías...")
    try:
        r = requests.get(URL_CATEGORIAS, headers=headers)
        data = r.json()
    except Exception as e:
        logging.error(f"Error categorías: {e}")
        return

    cats = []
    def extraer(items):
        for i in items:
            if i.get('id') and es_comida(i.get('name', '')):
                cats.append(i)
            if i.get('children'): extraer(i['children'])
            if i.get('subcategories'): extraer(i['subcategories'])
    
    raiz = data if isinstance(data, list) else data.get('data', [])
    extraer(raiz)
    logging.info(f"✅ Se encontraron {len(cats)} categorías objetivo.")

    # 2. Productos
    total_total = 0
    
    for cat in cats: 
        logging.info(f"📍 Procesando: {cat['name']} (ID: {cat['id']})")
        
        start = 0
        limit = 50 
        
        while True:
            params = {
                "category": cat['id'],
                "stock": "true",
                "start": start,
                "limit": limit
            }
            
            try:
                r = requests.get(URL_PRODUCTOS, headers=headers, params=params)
                
                if r.status_code == 200:
                    d = r.json()
                    
                    # --- CORRECCIÓN VITAL AQUÍ ---
                    # Tu log muestra que la clave correcta es 'results'
                    items = d.get('results') or d.get('products') or d.get('items') or []
                    
                    if not items:
                        # Si sigue vacío, es que realmente no hay productos en esa página
                        if start == 0: logging.warning(f"⚠️ Lista vacía real para {cat['name']}.")
                        break 

                    batch = []
                    for p in items:
                        # Extraer precio (usando amount_total como vimos en tu log)
                        precio = p.get('amount_total') or p.get('amount_incl_tax') or p.get('price') or 0
                        
                        # Extraer imagen
                        img = ""
                        if p.get('images') and len(p['images']) > 0: img = p['images'][0]
                        elif p.get('media') and len(p['media']) > 0: img = p['media'][0].get('url')

                        batch.append({
                            "supermarket": "Mi Comisariato",
                            "external_id": str(p.get('id')),
                            "name": p.get('name') or p.get('description'), 
                            "price": float(precio),
                            "image_url": img,
                            "category": cat['name']
                        })
                    
                    if batch:
                        send_to_backend(batch)
                        total_total += len(batch)
                        logging.info(f"   -> Procesados {len(batch)} items.")
                    
                    start += limit
                    time.sleep(1)

                elif r.status_code in [401, 403]:
                    logging.warning("Cookies caducadas.")
                    return 
                else:
                    break
                
            except Exception as e:
                logging.error(f"Excepción: {e}")
                break

    logging.info(f"🏁 Fin del ciclo. Total procesado: {total_total}")

if __name__ == "__main__":
    if wait_for_backend():
        while True:
            run_scraper()
            logging.info("💤 Durmiendo 1 hora...")
            time.sleep(3600)