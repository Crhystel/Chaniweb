import time
import requests
import logging
import os
from bs4 import BeautifulSoup 
from playwright.sync_api import sync_playwright

# --- CONFIGURACIÓN ---
API_URL = os.getenv("API_URL", "http://backend:8000/ingest/")
HEALTH_URL = os.getenv("API_URL", "http://backend:8000/products/").replace("/ingest/", "/products/")

URL_CATEGORIAS = "https://app.frecuento.com/categories/?image_quality=100"
URL_PRODUCTOS = "https://app.frecuento.com/products/"

AKI_URLS = [
    {"name": "Alacena-Canola", "url": "https://www.aki.com.ec/categoria/alacena/aceites-y-grasas-alacena/canola-aceites-y-grasas-alacena/"},
    {"name": "Alacena-Girasol", "url": "https://www.aki.com.ec/categoria/alacena/aceites-y-grasas-alacena/girasol-aceites-y-grasas-alacena/"},
    {"name": "Alacena-arroz", "url": "https://www.aki.com.ec/categoria/alacena/arroz-alacena/blanco-arroz-alacena/"},
   
]
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
                
import re # Asegúrate de tener esto arriba

def run_aki_scraper():
    logging.info("🚀 Iniciando extracción de AKI (MODO UBICACIÓN TUMBACO)...")
    
    # Coordenadas de GRAN AKI TUMBACO (Aprox)
    # Latitud: -0.2133, Longitud: -78.3996
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
            
            # --- AQUÍ ESTÁ EL TRUCO ---
            # Configuramos el navegador para que crea que está en Ecuador
            context = browser.new_context(
                viewport={'width': 1366, 'height': 768},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
                
                # 1. FALSIFICAR GEOLOCALIZACIÓN (Tumbaco)
                geolocation={"latitude": -0.2133, "longitude": -78.3996},
                permissions=["geolocation"], # Dar permiso automáticamente
                
                # 2. Configurar Idioma y Zona Horaria
                locale="es-EC",
                timezone_id="America/Guayaquil"
            )
            page = context.new_page()

            total_aki = 0

            for cat in AKI_URLS:
                logging.info(f"📍 AKI: Navegando a {cat['name']}...")
                
                try:
                    page.goto(cat['url'], timeout=90000, wait_until="domcontentloaded")
                    
                    # 3. MANEJO DE POPUP DE UBICACIÓN
                    # A veces sale un popup preguntando "¿Usar mi ubicación actual?"
                    # Esperamos un poco y tratamos de confirmar o cerrar
                    time.sleep(5) 
                    
                    try:
                        # Si sale un botón de "Usar mi ubicación", intentamos clickearlo
                        # (Ajusta el texto si el botón dice otra cosa)
                        ub_btn = page.get_by_text("Usar mi ubicación", exact=False)
                        if ub_btn.is_visible():
                            ub_btn.click()
                            time.sleep(3)
                        else:
                            # Si no, presionamos ESCAPE por si hay un modal bloqueante
                            page.keyboard.press("Escape")
                    except:
                        pass

                    # Esperar a que la red se calme (para que carguen los precios de esa tienda)
                    try:
                        page.wait_for_load_state("networkidle", timeout=10000)
                    except: pass

                    # 4. EXTRACCIÓN (Tu lógica Regex que ya funcionaba)
                    product_cards = page.locator('.product').all()
                    
                    if not product_cards:
                        logging.warning(f"   No se encontraron productos en {cat['name']}.")
                        continue

                    batch = []
                    for card in product_cards:
                        try:
                            # Nombre
                            name_el = card.locator('.woocommerce-loop-product__title').first
                            name = name_el.inner_text().strip() if name_el.count() > 0 else "Sin Nombre"

                            # Precio (Regex Robusto)
                            price = 0.0
                            full_text = card.inner_text()
                            
                            # Buscamos precios, priorizando los que parecen estar visibles
                            matches = re.findall(r'\$?\s?(\d+[\.,]\d{2})', full_text)
                            
                            if matches:
                                raw_price = matches[0]
                                clean_price = raw_price.replace(',', '.')
                                try: price = float(clean_price)
                                except: price = 0.0
                            
                            # Imagen
                            img_locator = card.locator('img').first
                            img_url = img_locator.get_attribute('src') if img_locator.count() > 0 else ""

                            # ID
                            import hashlib
                            ext_id = f"aki-{hashlib.md5(name.encode()).hexdigest()[:10]}"

                            if price > 0:
                                batch.append({
                                    "supermarket": "AKI", # Puedes poner "Gran AKI" si quieres
                                    "external_id": str(ext_id),
                                    "name": name,
                                    "price": price,
                                    "image_url": img_url,
                                    "category": "AKI-" + cat['name']
                                })

                        except Exception as e:
                            pass

                    if batch:
                        send_to_backend(batch)
                        total_aki += len(batch)
                        logging.info(f"   -> Enviados {len(batch)} productos de {cat['name']}.")
                    else:
                        logging.warning("   -> Productos vistos, pero sin precio legible.")
                            
                except Exception as e:
                    logging.error(f"Error procesando AKI {cat['name']}: {e}")
            
            browser.close()
            logging.info(f"🏁 AKI Finalizado. Total extraído: {total_aki}")

    except Exception as e:
        logging.error(f"Error fatal Playwright AKI: {e}")

if __name__ == "__main__":
    if wait_for_backend():
        while True:
            run_aki_scraper() 
            run_scraper()
            logging.info("💤 Durmiendo 1 hora...")
            time.sleep(3600)
            
        