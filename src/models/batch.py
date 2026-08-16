from typing import Any, Iterator, List, Optional, Union
from src.models.sale import SaleRecord


class Batch:
    """Yozuvlar to'plami (Batch) — konteynyer sinf."""

    def __init__(self, records: Optional[List[Any]] = None):
        """Ro'yxatni o'raydi. Agar records berilmasa, bo'sh ro'yxat yaratadi."""
        self.records: List[Any] = records if records is not None else []

    def add(self, record: Any) -> None:
        """To'plamga yangi yozuv qo'shadi."""
        self.records.append(record)

    def __len__(self) -> int:
        """len(batch) chaqirilganda elementlar sonini qaytaradi."""
        return len(self.records)

    def __iter__(self) -> Iterator[Any]:
        """'for r in batch' tsiklida ishlatish imkonini beradi."""
        return iter(self.records)

    def __getitem__(self, i: Union[int, slice]) -> Any:
        """batch[0] yoki batch[1:5] kabi indeksatsiyani qo'llab-quvvatlaydi."""
        return self.records[i]

    def __contains__(self, r: Any) -> bool:
        """'r in batch' deb tekshirish imkonini beradi."""
        return r in self.records

    def __bool__(self) -> bool:
        """'if batch:' tekshiruvida to'plam bo'sh bo'lmasa True qaytaradi."""
        return bool(self.records)

    def __repr__(self) -> str:
        """Debugging va loglar uchun ko'rinish."""
        return f"Batch(size={len(self)})"