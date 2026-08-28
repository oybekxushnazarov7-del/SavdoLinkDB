# sinov.py
from src.extract.csv_extractor import CsvExtractor
from src.extract.json_extractor import JsonExtractor

rows = list(CsvExtractor("data/incoming/sales_2026-01-02.csv").read())
keys = [k for k in rows[0] if not k.startswith("_")]
print("Birinchi kalit:", repr(keys[0]))
print("receipt_no    :", rows[0].get("receipt_no"))
