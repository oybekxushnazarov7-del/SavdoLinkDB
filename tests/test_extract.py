import json
import pytest
from src.extract.csv_extractor import CsvExtractor
from src.extract.json_extractor import JsonExtractor
from src.exceptions import ExtractError


def test_missing_and_empty_file(tmp_path):
    # Mavjud bo'lmagan fayl
    missing_file = tmp_path / "not_found.csv"
    with pytest.raises(ExtractError):
        CsvExtractor(missing_file)

    # Bo'sh fayl
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")
    with pytest.raises(ExtractError):
        CsvExtractor(empty_file)


def test_csv_extractor_with_header(tmp_path):
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("sku;name\nSKU-001;Sut\n", encoding="utf-8")

    extractor = CsvExtractor(csv_file)
    assert extractor.header() == ["sku", "name"]

    rows = list(extractor.read())
    assert len(rows) == 1
    assert rows[0]["sku"] == "SKU-001"
    assert rows[0]["_row_num"] == 2


def test_json_extractor_nested(tmp_path):
    json_file = tmp_path / "test.json"
    data = [
        {
            "sku": "SKU-001",
            "price_history": [
                {"valid_from": "2026-01-01", "price": 10000},
                {"valid_from": "2026-06-01", "price": 12000},
            ],
        }
    ]
    json_file.write_text(json.dumps(data), encoding="utf-8")

    extractor = JsonExtractor(json_file)
    records = list(extractor.read_nested(parent_key="sku", child_key="price_history"))

    assert len(records) == 2
    assert records[0]["sku"] == "SKU-001"
    assert records[0]["price"] == 10000