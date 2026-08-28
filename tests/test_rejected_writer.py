"""A-01 va D-8: rejected_writer json serializatsiyasi."""
import csv
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import pytest

from src.validate.rejected_writer import RejectedWriter, _json_default
from src.validate.validator import ValidationResult
from src.validate.rules import PriceIsNumericRule


def test_json_default_datetime_and_decimal():
    assert _json_default(datetime(2026, 1, 1, 19, 0)) == "2026-01-01T19:00:00"
    assert _json_default(Decimal("18500.00")) == "18500.00"


def test_rejected_writer_uses_raw_not_transformed(tmp_path):
    """raw_row fayldagi asl matnni saqlashi kerak."""
    path = tmp_path / "rejected.csv"
    raw = {
        "unit_price": "18500,00",
        "sale_datetime": "01.01.2026 19:00",
        "sku": "SKU-00001",
    }
    transformed = {
        "unit_price": Decimal("18500.00"),
        "sale_datetime": datetime(2026, 1, 1, 19, 0),
        "sku": "SKU-00001",
        "_raw": raw,
    }
    result = ValidationResult(record=transformed, errors=[PriceIsNumericRule()])

    with RejectedWriter(path, "LOAD-TEST") as writer:
        writer.write(result, "sales_2026-01-01.csv", 5)

    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1
    raw_row = json.loads(rows[0]["raw_row"])
    assert raw_row["unit_price"] == "18500,00"
    assert raw_row["sale_datetime"] == "01.01.2026 19:00"
