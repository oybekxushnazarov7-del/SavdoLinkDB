import json
from pathlib import Path
from typing import Any, Dict
from src.exceptions import ConfigError

def load_settings(path: str="config/settings.json") -> dict:
    file_path = Path(path)
    if file_path and (not file_path.exists()):
        raise ConfigError(f"Sozlamalar fayli topilmadi: {path}")

    try:
        with open(file_path,'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"JSON faylini o'qishda xatolik: {e}")

class Config():
    def __init__(self,data):
        if not isinstance(data, dict):
            raise ConfigError(f"Data lug'at ko'rinishida bo'lishi kerak")
        self._data = data

    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split(".")
        current = self._data
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
        

    def require(self, key: str) -> Any:
        value = self.get(key)
        if value is None:
            raise ConfigError(f"Key qiymat topilmadi ! ")
        return value

    @property
    def paths(self) -> Dict[str, Path]:
        raw_paths = self.get("paths", {})
        if not isinstance(raw_paths, dict):
            return {}

        return {k: Path(v) for k, v in raw_paths.items()}
    
