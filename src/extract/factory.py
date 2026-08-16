from pathlib import Path
from typing import Union, Dict, Type
from src.extract.base_extractor import BaseExtractor
from src.extract.csv_extractor import CsvExtractor
from src.extract.json_extractor import JsonExtractor
from src.exceptions import ExtractError

# Extractor sinflarini kengaytmalar bilan bog'laydigan xarita
EXTRACTORS: Dict[str, Type[BaseExtractor]] = {
    ".csv": CsvExtractor,
    ".json": JsonExtractor,
}


def get_extractor(
    path: Union[str, Path], config: any = None
) -> BaseExtractor:
    """
    Fayl kengaytmasiga qarab tegishli extractor obyektini yaratib qaytaradi.
    """
    file_path = Path(path)
    ext = file_path.suffix.lower()

    extractor_cls = EXTRACTORS.get(ext)
    if not extractor_cls:
        raise ExtractError(
            file_path, f"Qo'llab-quvvatlanmaydigan fayl formati: {ext}"
        )

    return extractor_cls(file_path)