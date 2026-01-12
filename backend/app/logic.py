import re
from sqlalchemy.sql import func
from . import models

def normalize_and_save(db, product_in: models.ProductCreate):
    # 1. Detectar unidad y cantidad (Regex)
    # Busca patrones como "180g", "1 kg", "2.5 Litros"
    pattern = r"(\d+(?:\.\d+)?)\s*(g|gr|kg|ml|l|lb|oz)"
    match = re.search(pattern, product_in.name, re.IGNORECASE)
    
    quantity = 1.0
    unit = "unidad"
    price_per_unit = product_in.price
    
    if match:
        qty_str, unit_str = match.groups()
        quantity = float(qty_str)
        unit = unit_str.lower()
        
        # Estandarización a KG y Litros
        if unit in ['g', 'gr']:
            quantity /= 1000
            unit = 'kg'
        elif unit == 'ml':
            quantity /= 1000
            unit = 'l'
        
        # Calcular precio unitario para comparaciones reales
        if quantity > 0:
            price_per_unit = product_in.price / quantity

    # 2. Guardar o Actualizar en BD
    existing = db.query(models.ProductDB).filter(
        models.ProductDB.external_id == product_in.external_id,
        models.ProductDB.supermarket == product_in.supermarket
    ).first()

    if existing:
        existing.price = product_in.price
        existing.updated_at = func.now()
    else:
        # Aquí estaba el error. Lo hacemos explícito campo por campo:
        new_prod=models.ProductDB(
            external_id=product_in.external_id,
            name=product_in.name,
            supermarket=product_in.supermarket,
            price=product_in.price,
            image_url=product_in.image_url,
            normalized_name=product_in.name.upper(),
            quantity=quantity,
            unit=unit,
            price_per_unit=price_per_unit
        )
        db.add(new_prod)
    
    db.commit()