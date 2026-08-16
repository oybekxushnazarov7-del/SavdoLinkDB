import csv
import json
from pathlib import Path
from typing import Optional, Union

from src.validate.validator import ValidationResult


class RejectedWriter:
    """Rad etilgan yozuvlarni audit uchun alohida CSV fayliga yozuvchi sinf."""

    FIELDNAMES = [
        "load_id",
        "source_file",
        "row_num",
        "rule_code",
        "rule_message",
        "raw_row",
    ]

    def __init__(self, path: Union[str, Path], load_id: str) -> None:
        """Fayl yo'lini va yuklash identifikatorini (load_id) tayyorlaydi."""
        self.path = Path(path)
        self.load_id = load_id
        self._count = 0
        self._file = None
        self._writer = None

    def __enter__(self) -> "RejectedWriter":
        """Kontekst menejer: faylni ochadi va CSV header yozadi."""
        # Papka mavjud bo'lmasa, uni yaratish
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._file = open(self.path, mode="w", newline="", encoding="utf-8")
        self._writer = csv.DictWriter(self._file, fieldnames=self.FIELDNAMES)
        self._writer.writeheader()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Kontekst menejer: faylni xavfsiz yopadi."""
        if self._file:
            self._file.close()
            self._file = None

    def write(
        self,
        result: ValidationResult,
        source_file: str = "",
        row_num: Optional[int] = None,
    ) -> None:
        """Bitta rad etilgan yozuvni va unga tegishli barcha ERROR qoidalarini CSV fayliga yozadi."""
        if not self._writer:
            raise RuntimeError(
                "RejectedWriter 'with' kontekst menejeri ichida ishlatilishi kerak."
            )

        # Agar yaroqli bo'lsa (ERROR yo'q), rad etilganlar fayliga yozilmaydi
        if result.is_valid:
            return

        # Yozuvdagi asl ma'lumotni saqlash (dict bo'lsa JSON string shaklida)
        raw_row_str = (
            json.dumps(result.record, ensure_ascii=False)
            if isinstance(result.record, dict)
            else str(result.record)
        )

        # Bitta qatorda bir nechta ERROR bo'lishi mumkin: har biri uchun alohida yozuv tushiriladi
        for error in result.errors:
            row_data = {
                "load_id": self.load_id,
                "source_file": source_file,
                "row_num": row_num if row_num is not None else "",
                "rule_code": error.code,
                "rule_message": error.message,
                "raw_row": raw_row_str,
            }
            self._writer.writerow(row_data)
            self._count += 1

    @property
    def count(self) -> int:
        """Faylga yozilgan rad etilgan qatorlar sonini qaytaradi."""
        return self._count

