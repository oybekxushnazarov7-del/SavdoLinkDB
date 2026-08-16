from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional
from src.models.money import Money


@dataclass(frozen=True)
class PricePoint:
    """Narx nuqtasi: ma'lum bir sanadan boshlab amal qiladigan narx."""
    valid_from: date
    price: Money


@dataclass
class Product:
    """Mahsulot obyekti va uning narxlar tarixi."""
    sku: str                          # Tabiiy kalit (masalan, 'PRD-001')
    name: str                         # Mahsulot nomi
    category_code: str                # Kategoriya kodi
    supplier_inn: str                 # Ta'minotchi INN
    unit: str                         # O'lchov birligi (dona, kg, va h.k.)
    prices: List[PricePoint] = field(default_factory=list)  # Narx tarixi

    def price_at(self, on_date: date) -> Optional[Money]:
        """
        Berilgan 'on_date' sanasida amalda bo'lgan narxni qaytaradi.
        Sana bo'yicha saralab, berilgan sanaga teng yoki undan oldingi eng oxirgi narxni oladi.
        """
        valid_prices = [p for p in self.prices if p.valid_from <= on_date]
        if not valid_prices:
            return None
        
        # valid_from bo'yicha eng oxirgi amal qilgan narxni topish
        latest_price_point = max(valid_prices, key=lambda p: p.valid_from)
        return latest_price_point.price

    def __eq__(self, other) -> bool:
        """sku bo'yicha tenglikni tekshiradi."""
        if isinstance(other, Product):
            return self.sku == other.sku
        return False

    def __hash__(self) -> int:
        """sku bo'yicha hash hisoblaydi."""
        return hash(self.sku)

    def __repr__(self) -> str:
        """Nosozlikni tuzatish (debugging) uchun qulay korinish."""
        return f"Product(sku={self.sku!r}, name={self.name!r}, unit={self.unit!r})"