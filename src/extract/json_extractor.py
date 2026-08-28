import json
from typing import Generator, Dict, Any
from src.extract.base_extractor import BaseExtractor


class JsonExtractor(BaseExtractor):
    """JSON fayllardan ma'lumotlarni o'quvchi extractor."""

    def read(self) -> Generator[Dict[str, Any], None, None]:
        """JSON fayldagi asosiy massiv elementlarini birma-bir qaytaradi."""
        with open(self.path, encoding="utf-8-sig") as f:
            data = json.load(f)

            # Agar JSON obyektlar ro'yxati (list) bo'lsa
            if isinstance(data, list):
                for row_num, item in enumerate(data, start=1):
                    if isinstance(item, dict):
                        item["_source_file"] = self.path.name
                        item["_row_num"] = row_num
                        yield item

    def read_nested(
        self, parent_key: str, child_key: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Ichma-ich kelgan massivni yassilaydi (flatten qiladi).
        Masalan: {sku: "SKU-001", price_history: [{...}, {...}]} obyektdan
        har bir narx tarixi uchun alohida yozuv hosil qiladi.
        """
        with open(self.path, encoding="utf-8-sig") as f:
            data = json.load(f)

            if isinstance(data, list):
                row_num = 1
                for item in data:
                    if isinstance(item, dict) and child_key in item:
                        # Asosiy kalitni olish (masalan, sku)
                        parent_val = item.get(parent_key)
                        child_list = item.get(child_key, [])

                        if isinstance(child_list, list):
                            for child_item in child_list:
                                if isinstance(child_item, dict):
                                    record = {
                                        parent_key: parent_val,
                                        **child_item,
                                        "_source_file": self.path.name,
                                        "_row_num": row_num,
                                    }
                                    row_num += 1
                                    yield record