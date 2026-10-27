import json
import logging
import os

logger = logging.getLogger(__name__)

_DATA = os.path.join(os.path.dirname(__file__), "products.json")

with open(_DATA) as f:
    PRODUCTS = json.load(f)

def search_product(query: str) -> str:
    q = query.lower()
    results = [p for p in PRODUCTS if q in p["name"].lower() or q in p["description"].lower()]
    if not results:
        return "No products found."
    return "\n".join(f"{p['id']}: {p['name']} - {p['description']} ({p['price']:,} RWF)" for p in results)

def check_price(product_id: str) -> str:
    try:
        pid = product_id.strip().upper()
        for p in PRODUCTS:
            if p["id"] == pid:
                logger.info(f"Price check: {pid} = {p['price']} RWF")
                return f"{p['name']} costs {p['price']:,} RWF"
        logger.warning(f"Product not found: {pid}")
        return f"Product {product_id} not found."
    except Exception as e:
        logger.error(f"check_price error: {e}")
        return f"Error: {str(e)}"
