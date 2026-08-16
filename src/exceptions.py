class SavdoLinkError(Exception):
    """Loyihadagi barcha xatolarning bazasi."""
    pass


class ExtractError(SavdoLinkError):
    """Fayl o'qishda yuzaga kelgan xato."""

    def __init__(self, path, reason):
        self.path = path
        self.reason = reason
        super().__init__(f"{path}: {reason}")

class ConfigError(SavdoLinkError):
    def __init__(self, key, reason):
        self.key = key
        self.reason = reason
        super().__init__(f"{key}:{reason}")
