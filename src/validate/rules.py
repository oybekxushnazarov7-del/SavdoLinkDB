from datetime import date, datetime
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
        sku = record.get("sku")
        return sku is not None and str(sku).strip() != ""


class DateRequiredRule(ValidationRule):
    code = "DATE_REQUIRED"
    message = "Sana ko'rsatilishi shart"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        return record.get("date") is not None


# ==============================================================================
# 2. TIP QOIDALARI (Type validation checks)
# ==============================================================================

class QtyIsIntRule(ValidationRule):
    code = "QTY_IS_INT"
    message = "Miqdor butun son bo'lishi kerak"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        qty = record.get("qty")
        return isinstance(qty, int)


class PriceIsNumericRule(ValidationRule):
    code = "PRICE_IS_NUMERIC"
    message = "Narx son ko'rinishida bo'lishi kerak"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        price = record.get("price")
        return isinstance(price, (int, float)) and not isinstance(price, bool)


# ==============================================================================
# 3. DIAPAZON QOIDALARI (Range checks)
# ==============================================================================

class QtyPositiveRule(ValidationRule):
    code = "QTY_POSITIVE"
    message = "Miqdor 0 dan katta bo'lishi kerak"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        qty = record.get("qty")
        return qty is not None and isinstance(qty, (int, float)) and qty > 0


class DiscountRangeRule(ValidationRule):
    code = "DISCOUNT_RANGE"
    message = "Chegirma 0% va 100% oralig'ida bo'lishi kerak"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        discount = record.get("discount", 0)
        if discount is None:
            return True  # Chegirma bo'lmasa qoida buzilmadi deb hisoblanadi
        return 0 <= discount <= 100


# ==============================================================================
# 4. MANTIQ QOIDALARI (Cross-field logic checks)
# ==============================================================================

class ReturnAfterSaleRule(ValidationRule):
    code = "RETURN_AFTER_SALE"
    message = "Qaytarish sanasi sotuv sanasidan oldin bo'lishi mumkin emas"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        sale_date = record.get("sale_date") or record.get("date")
        return_date = record.get("return_date")

        if not sale_date or not return_date:
            return True  # Har ikkala sana ham mavjud bo'lgandagina mantiqiy tekshiriladi

        return return_date >= sale_date


# ==============================================================================
# 5. REFERENSIAL QOIDALAR (Reference checks)
# ==============================================================================

class SkuExistsRule(ValidationRule):
    code = "SKU_EXISTS"
    message = "Mahsulot katalogda topilmadi"
    severity = "ERROR"

    def check(self, record: dict) -> bool:
        # catalogue_price mavjudligi orqali katalogda mahsulot borligi tekshiriladi
        # (enrichers.py jarayonidan keyin)
        return record.get("catalog_price") is not None or record.get("in_catalog") is True


# ==============================================================================
# 6. BIZNES QOIDALARI (Business logic / Anomalies checks)
# ==============================================================================

class PriceDeviationRule(ValidationRule):
    code = "PRICE_DEVIATION"
    message = "Sotuv narxi katalog narxidan keskin farq qiladi"
    severity = "WARNING"

    def check(self, record: dict) -> bool:
        sale_price = record.get("price")
        catalog_price = record.get("catalog_price")

        if sale_price is None or catalog_price is None or catalog_price == 0:
            return True

        # Narx o'rtasidagi farq 50% dan yuqori bo'lsa ogohlantirish beradi
        deviation = abs(sale_price - catalog_price) / catalog_price
        return deviation <= 0.50 