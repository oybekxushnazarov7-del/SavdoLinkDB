from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union


class PriceCatalog:
    def __init__(self, products: List[Any]) -> None:
        self._catalog: Dict[str, Any] = {}
        for p in products:
            sku = getattr(p, "sku", None) if hasattr(p, "sku") else p.get("sku")
            if sku:
                self._catalog[str(sku).strip().upper()] = p

    def price_at(self, sku: str, on_date: date) -> Optional[Any]:
        product = self._catalog.get(str(sku).strip().upper() if sku else "")
        if not product:
            return None

        if hasattr(product, "price_at") and callable(getattr(product, "price_at")):
            return product.price_at(on_date)

        if hasattr(product, "price"):
            return getattr(product, "price")

        if isinstance(product, dict):
            # price_history bo'lsa — sanaga mos narx
            history = product.get("price_history") or []
            if history and on_date is not None:
                applicable = [
                    h for h in history
                    if h.get("valid_from") and str(h["valid_from"]) <= str(on_date)
                ]
                if applicable:
                    best = max(applicable, key=lambda h: str(h["valid_from"]))
                    return best.get("price")
            return product.get("price")

        return None

    def __contains__(self, sku: str) -> bool:
        return str(sku).strip().upper() in self._catalog if sku else False


def enrich_sale(
    record: Dict[str, Any],
    catalog: PriceCatalog,
    stores: Dict[str, Any],
    employees: Dict[str, Any],
) -> Dict[str, Any]:
    """Sotuv yozuviga katalog / do'kon / xodim ma'lumotlarini qo'shadi."""
    enriched_record = record.copy()

    # P-13: "date" / "employee_id" emas — sale_datetime / cashier_id
    sku = record.get("sku")
    sale_date = record.get("sale_datetime")
    if hasattr(sale_date, "date"):
        sale_date = sale_date.date()
    elif isinstance(sale_date, datetime):
        sale_date = sale_date.date()

    if sku and sku in catalog:
        catalog_price = catalog.price_at(sku, on_date=sale_date)
        enriched_record["catalog_price"] = catalog_price
        enriched_record["in_catalog"] = True
        if enriched_record.get("unit_price") is None and catalog_price is not None:
            enriched_record["unit_price"] = catalog_price
            enriched_record["_price_source"] = "catalog"
    else:
        enriched_record["in_catalog"] = False

    if enriched_record.get("unit_price") is not None and "_price_source" not in enriched_record:
        enriched_record["_price_source"] = "file"

    store_code = record.get("store_code") or record.get("store_id")
    if store_code and store_code in stores:
        store_info = stores[store_code]
        if isinstance(store_info, dict):
            enriched_record["store_name"] = store_info.get("name") or store_info.get("store_name")
            enriched_record["store_region"] = store_info.get("region")
        else:
            enriched_record["store_info"] = store_info

    cashier_id = record.get("cashier_id")
    if cashier_id and cashier_id in employees:
        emp_info = employees[cashier_id]
        if isinstance(emp_info, dict):
            enriched_record["employee_name"] = emp_info.get("name") or emp_info.get("full_name")
            enriched_record["employee_role"] = emp_info.get("role") or emp_info.get("position")
            # CashierStoreRule uchun
            enriched_record["cashier_store_code"] = emp_info.get("store_code")
        else:
            enriched_record["employee_info"] = emp_info

    return enriched_record
