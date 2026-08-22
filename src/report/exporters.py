"""
Vazifasi: Ma'lumotlarni CSV va JSON ko'rinishida eksport qilish.
"""
import csv
import json
from pathlib import Path
from decimal import Decimal
from datetime import date, datetime

def json_default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Aylantirib bo'lmadi: {type(obj)}")

def to_csv(rows: list[dict], path: Path) -> Path:
    if not rows:
        return path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode="w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path

def to_json(data: dict | list, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, mode="w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=json_default)
    return path