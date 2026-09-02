from datetime import date, datetime
from decimal import Decimal  # PriceIsNumericRule uchun — import yetishmagan edi
from typing import Any, Dict


# ==============================================================================
# BAZAVIY SINF
# ==============================================================================

class ValidationRule:
    """Bitta biznes qoidasi.

    Har bir qoida BITTA narsani tekshiradi. Ikkita shart bo'lsa - ikkita qoida.
    """

    code: str = ""
    message: str = ""
    severity: str = "ERROR"  # "ERROR" -> rad etish, "WARNING" -> ogohlantirish

    def check(self, record: dict) -> bool:
        """True - qoida bajarilgan, False - buzilgan."""
        raise NotImplementedError

    def __call__(self, record: dict) -> bool:
        return self.check(record)

    def __repr__(self) -> str:
        return f"<{self.code} {self.severity}>"


# ==============================================================================
# 1. MAJBURIYLIK QOIDALARI (Required checks)
# ==============================================================================

class SkuRequiredRule(ValidationRule):
    code = "SKU_REQUIRED"
    message = "SKU kodi kiritilishi shart"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        # P-12: CSV/transform kaliti — sku
        sku = record.get("sku")
        return sku is not None and str(sku).strip() != ""


class SaleDateRequiredRule(ValidationRule):
    # P-12: DateRequiredRule / "date" o'rniga sale_datetime
    code = "DATE_REQUIRED"
    message = "Sana ko'rsatilishi shart"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        return record.get("sale_datetime") is not None


# Eski importlar uchun alias (testlar/eski kod)
DateRequiredRule = SaleDateRequiredRule


# ==============================================================================
# 2. TIP QOIDALARI (Type validation checks)
# ==============================================================================

class QtyIsIntRule(ValidationRule):
    code = "QTY_IS_INT"
    message = "Miqdor butun son bo'lishi kerak"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        qty = record.get("qty")
        return isinstance(qty, int) and not isinstance(qty, bool)


class PriceIsNumericRule(ValidationRule):
    code = "PRICE_IS_NUMERIC"
    message = "Narx son ko'rinishida bo'lishi kerak"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        # P-12: "price" emas — unit_price
        price = record.get("unit_price")
        return isinstance(price, (int, float, Decimal)) and not isinstance(price, bool)


# ==============================================================================
# 3. DIAPAZON QOIDALARI (Range checks)
# ==============================================================================

class QtyPositiveRule(ValidationRule):
    code = "QTY_POSITIVE"
    message = "Miqdor 0 dan katta bo'lishi kerak"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        qty = record.get("qty")
        return isinstance(qty, int) and not isinstance(qty, bool) and qty > 0


class DiscountRangeRule(ValidationRule):
    code = "DISCOUNT_RANGE"
    message = "Chegirma 0% va 100% oralig'ida bo'lishi kerak"
    severity = "ERROR"

    def __init__(self, min_pct: float = 0, max_pct: float = 100):
        self.min_pct = min_pct
        self.max_pct = max_pct

    def check(self, record: dict) -> bool:
        # P-12: "discount" emas — discount_pct
        discount = record.get("discount_pct")
        if discount is None:
            return True
        try:
            return self.min_pct <= float(discount) <= self.max_pct
        except (TypeError, ValueError):
            return False


# ==============================================================================
# 4. MANTIQ QOIDALARI (Cross-field logic checks)
# ==============================================================================

class ReturnAfterSaleRule(ValidationRule):
    code = "RETURN_AFTER_SALE"
    message = "Qaytarish sanasi sotuv sanasidan oldin bo'lishi mumkin emas"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        # P-12: sale_datetime
        sale_date = record.get("sale_datetime")
        return_date = record.get("return_date")

        if not sale_date or not return_date:
            return True

        return return_date >= sale_date


class CashierStoreRule(ValidationRule):
    # P-14: validation_rules.json dagi CASHIER_STORE — sinf yo'q edi
    code = "CASHIER_STORE"
    message = "Kassir o'zi biriktirilmagan do'konda savdo qilmoqda"
    severity = "WARNING"

    def check(self, record: dict) -> bool:
        expected = record.get("cashier_store_code")
        actual = record.get("store_code")
        if expected is None or actual is None:
            return True  # boyitish bo'lmasa ogohlantirmaymiz
        return str(expected).strip().upper() == str(actual).strip().upper()


# ==============================================================================
# 5. REFERENSIAL QOIDALAR (Reference checks)
# ==============================================================================

class SkuExistsRule(ValidationRule):
    code = "SKU_EXISTS"
    message = "Mahsulot katalogda topilmadi"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        # enrichers.py dan keyin catalog_price / in_catalog
        return record.get("catalog_price") is not None or record.get("in_catalog") is True


class StoreExistsRule(ValidationRule):
    """Do'kon kodi spravochnikda bormi."""
    code = "STORE_EXISTS"
    message = "Do'kon kodi mavjud emas"
    severity = "ERROR"

    def __init__(self, known_stores=None):
        self.known_stores = known_stores or set()

    def check(self, record: dict) -> bool:
        if not self.known_stores:
            return True
        return (record.get("store_code") or "").strip().upper() in self.known_stores


class FutureDateRule(ValidationRule):
    """Savdo sanasi kelajakda bo'lmasligi kerak."""
    code = "FUTURE_DATE"
    message = "Savdo sanasi kelajakda"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        dt = record.get("sale_datetime")
        if dt is None:
            return True
        value = dt.date() if hasattr(dt, "date") else dt
        return value <= date.today()


# ==============================================================================
# 6. BIZNES QOIDALARI (Business logic / Anomalies checks)
# ==============================================================================

class PriceDeviationRule(ValidationRule):
    code = "PRICE_DEVIATION"
    message = "Sotuv narxi katalog narxidan keskin farq qiladi"
    severity = "WARNING"

    def __init__(self, max_factor: float = 1.5):
        # P-15: chegara kodda 0.50 qattiq yozilmasin — konfiguratsiyadan keladi
        self.max_factor = max_factor

    def check(self, record: dict) -> bool:
        # P-12: unit_price
        sale_price = record.get("unit_price")
        catalog_price = record.get("catalog_price")

        if sale_price is None or catalog_price is None or catalog_price == 0:
            return True

        try:
            sale = float(sale_price)
            catalog = float(catalog_price)
        except (TypeError, ValueError):
            return True

        return abs(sale - catalog) / catalog <= (self.max_factor - 1)


# P-04: Validator argumentsiz chaqirilmasin — DEFAULT_RULES oshkora uzatiladi
DEFAULT_RULES = [
    SkuRequiredRule(),
    SaleDateRequiredRule(),
    QtyIsIntRule(),
    QtyPositiveRule(),
    PriceIsNumericRule(),
    DiscountRangeRule(),
    PriceDeviationRule(),
]
