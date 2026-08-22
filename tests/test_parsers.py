"""
Fayl: tests/test_parsers.py
Vazifasi: Ma'lumotlarni o'tkazish (parsing) funksiyalarini sinash.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from src.transform.parsers import parse_datetime, parse_decimal, parse_int

@pytest.mark.parametrize("value,expected", [
    ("2026-03-14 09:12:33", datetime(2026, 3, 14, 9, 12, 33)),
    ("14.03.2026 09:12",    datetime(2026, 3, 14, 9, 12)),
    ("",                    None),
    ("   ",                 None),
    ("aniq emas",           None),
    (None,                  None),
])
def test_parse_datetime(value, expected):
    assert parse_datetime(value) == expected

@pytest.mark.parametrize("value,expected", [
    ("18500.50", Decimal("18500.50")),
    ("18 500,50", Decimal("18500.50")),
    ("0",         Decimal("0")),
    ("-12.5",     Decimal("-12.5")),
    ("abc",       None),
    (None,        None),
])
def test_parse_decimal(value, expected):
    assert parse_decimal(value) == expected

def test_parse_int():
    assert parse_int("123") == 123
    assert parse_int(" 45 ") == 45
    assert parse_int("invalid") is None