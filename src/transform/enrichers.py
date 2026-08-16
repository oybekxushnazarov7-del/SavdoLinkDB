from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

class PriceCatalog:
    def __init__(self, products: List[Any]) -> None:
            self._catalog: Dict[str, Any] = {}
            for p in products:
                sku = getattr(p, "sku", None) if hasattr(p, "sku") else p.get("sku")
                if sku:
                    self._catalog[sku] = p

    def price_at(self,sku: str, on_date: date) -> bool:
        product = self._catalog.get(sku)
        if not product:
            return None

        # Agar product obyekt bo'lsa:
        if hasattr(product, "price_at") and callable(getattr(product, "price_at")):
            return product.price_at(on_date)
        
        if hasattr(product, "price"):
            return getattr(product, "price")

        # Agar product lug'at (dict) bo'lsa:
        if isinstance(product, dict):
            return product.get("price")

        return None

    def __contains__(self, sku: str) -> bool:
        """'sku in catalog' shaklida tekshirish imkoniyatini beradi."""
        return sku in self._catalog 

def enrich_sale(
    record: Dict[str, Any],
    catalog: PriceCatalog,
    stores: Dict[str, Any],
    employees: Dict[str, Any],
) -> Dict[str, Any]:
    """Sotuv yozuviga katalog, do'konlar va xodimlar ma'lumotlaridan olingan qiymatlarni birlashtiradi (enrichment)."""
    enriched_record = record.copy()

    sku = record.get("sku")
    sale_date = record.get("date")  # Masalan, 'date' kalitida sana saqlangan bo'lsa

    # 1. Narx va katalog ma'lumotlarini qo'shish
    if sku and sku in catalog:
        catalog_price = catalog.price_at(sku, on_date=sale_date)
        enriched_record["catalog_price"] = catalog_price
        
        # Agar sotuv narxi bo'lmasa, katalog narxini ishlatish
        if enriched_record.get("price") is None:
            enriched_record["price"] = catalog_price

    # 2. Do'kon ma'lumotlarini qo'shish (store_code yoki store_id bo'yicha)
    store_code = record.get("store_code") or record.get("store_id")
    if store_code and store_code in stores:
        store_info = stores[store_code]
        if isinstance(store_info, dict):
            enriched_record["store_name"] = store_info.get("name")
            enriched_record["store_region"] = store_info.get("region")
        else:
            enriched_record["store_info"] = store_info

    # 3. Xodim ma'lumotlarini qo'shish (employee_id bo'yicha)
    employee_id = record.get("employee_id")
    if employee_id and employee_id in employees:
        emp_info = employees[employee_id]
        if isinstance(emp_info, dict):
            enriched_record["employee_name"] = emp_info.get("name")
            enriched_record["employee_role"] = emp_info.get("role")
        else:
            enriched_record["employee_info"] = emp_info

    return enriched_record