import csv
from typing import Generator, List, Dict, Any
from src.extract.base_extractor import BaseExtractor


class CsvExtractor(BaseExtractor):
    """CSV fayllardan ma'lumotlarni qatorma-qator o'quvchi extractor."""

    def __init__(self, path: str, delimiter: str = ";", encoding: str = "utf-8"):
        super().__init__(path, encoding)
        self.delimiter = delimiter

    def read(self) -> Generator[Dict[str, Any], None, None]:
        """
        CSV faylni o'qib, har bir qatorni lug'at (dict) ko'rinishida qaytaradi.
        Yangi ma'lumotlar bilan boyitadi: '_source_file' va '_row_num'.
        """
        with open(self.path, encoding=self.encoding, newline="") as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            
            # Sarlavha 1-qatorni egallaydi, shuning uchun ma'lumotlar 2-qatordan boshlanadi
            for row_num, row in enumerate(reader, start=2):
                row["_source_file"] = self.path.name
                row["_row_num"] = row_num
                yield row

    def header(self) -> List[str]:
        """CSV faylining ustun nomlari (sarlavhalari) ro'yxatini qaytaradi."""
        with open(self.path, encoding=self.encoding, newline="") as f:
            reader = csv.reader(f, delimiter=self.delimiter)
            return next(reader, [])