from dataclasses import dataclass
from typing import Tuple


@dataclass
class SaleRecord:
    """Extract (S2) bosqichidagi xom sotuv yozuvi."""
    receipt_no: str         # Chek raqami (xom holda)
    store_code: str         # Do'kon kodi
    cashier_id: str         # Kassir
    sale_datetime_raw: str  # Xom matn — hali sanaga aylantirilmagan
    sku: str                # Mahsulot
    qty_raw: str            # Xom matn
    unit_price_raw: str     # Xom matn
    discount_raw: str       # Xom matn
    payment_type: str       # To'lov turi
    source_file: str        # Qaysi fayldan
    row_num: int            # Nechanchi qator

    def unique_key(self) -> Tuple[str, str]:
        """Dublikatlarni aniqlash uchun unikal kalit qaytaradi."""
        return (self.receipt_no, self.sku)

    def __eq__(self, other) -> bool:
        """unique_key() ga tayanib tenglikni tekshiradi."""
        if isinstance(other, SaleRecord):
            return self.unique_key() == other.unique_key()
        return False

    def __hash__(self) -> int:
        """unique_key() ga tayanib hash hisoblaydi."""
        return hash(self.unique_key())

    def __repr__(self) -> str:
        """Debugging va loglar uchun qulay ko'rinish."""
        return (
            f"SaleRecord(receipt_no={self.receipt_no!r}, "
            f"sku={self.sku!r}, row={self.row_num})"
        )