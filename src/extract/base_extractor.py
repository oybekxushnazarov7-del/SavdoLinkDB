from abc import ABC, abstractmethod
from pathlib import Path
from src.exceptions import ExtractError


class BaseExtractor(ABC):
    """Barcha extractorlarning bazasi.

    Umumiy tekshiruvlar shu yerda. Voris sinflar faqat read() ni yozadi.
    """

    def __init__(self, path, encoding="utf-8-sig"):
        self.path = Path(path)
        self.encoding = encoding
        
        # Fayl diskda mavjudligini va bo'sh emasligini tekshirish
        if not self.path.exists():
            raise ExtractError(self.path, "fayl topilmadi")
        if self.path.stat().st_size == 0:
            raise ExtractError(self.path, "fayl bo'sh")

    @abstractmethod
    def read(self):
        """Yozuvlarni birma-bir qaytaradi (generator)."""
        pass

    def __iter__(self):
        """Extractor ustida to'g'ridan-to'g'ri tsikl (for) ishlatish imkonini beradi."""
        return self.read()

    def __repr__(self):
        """Debugging va loglash uchun qulay ko'rinish qaytaradi."""
        return f"{type(self).__name__}({self.path.name!r})"
