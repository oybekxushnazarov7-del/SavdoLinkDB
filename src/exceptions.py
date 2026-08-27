# P-03: ConfigError ikkita argument talab qilmasligi kerak —
# chaqiruvlar faqat xabar matni uzatadi.
class SavdoLinkError(Exception):
    """Loyihadagi barcha xatolarning bazasi."""


class ConfigError(SavdoLinkError):
    """Sozlama fayli yo'q yoki noto'g'ri."""


class ExtractError(SavdoLinkError):
    """Fayl o'qishda yuzaga kelgan xato."""

    def __init__(self, path, reason):
        self.path = path
        self.reason = reason
        super().__init__(f"{path}: {reason}")


class ValidationError(SavdoLinkError):
    """Ma'lumot qoidaga zid."""


class LoadError(SavdoLinkError):
    """Bazaga yozishda xato."""
