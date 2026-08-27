"""
Fayl: tests/test_rules.py
Vazifasi: src/validate/rules.py — P-12 ustun nomlari bilan.
"""
from datetime import datetime, timedelta
from decimal import Decimal
import pytest

from src.validate.rules import (
    SaleDateRequiredRule,
    DiscountRangeRule,
    PriceDeviationRule,
    PriceIsNumericRule,
    QtyIsIntRule,
    QtyPositiveRule,
    ReturnAfterSaleRule,
    SkuExistsRule,
    SkuRequiredRule,
    CashierStoreRule,
    ValidationRule,
)


def test_base_validation_rule_not_implemented():
    class CustomRule(ValidationRule):
        pass

    rule = CustomRule()
    with pytest.raises(NotImplementedError):
        rule.check({"test": "data"})


def test_sku_required_rule():
    rule = SkuRequiredRule()
    assert rule.check({"sku": "SKU12345"}) is True
    assert rule.check({"sku": ""}) is False
    assert rule.check({"sku": "   "}) is False
    assert rule.check({}) is False


def test_sale_date_required_rule():
    rule = SaleDateRequiredRule()
    assert rule.check({"sale_datetime": datetime(2026, 3, 14)}) is True
    assert rule.check({"sale_datetime": None}) is False
    assert rule.check({}) is False


def test_qty_is_int_rule():
    rule = QtyIsIntRule()
    assert rule.check({"qty": 10}) is True
    assert rule.check({"qty": "10"}) is False
    assert rule.check({"qty": 10.5}) is False


def test_price_is_numeric_rule():
    rule = PriceIsNumericRule()
    assert rule.check({"unit_price": 100}) is True
    assert rule.check({"unit_price": Decimal("99.99")}) is True
    assert rule.check({"unit_price": True}) is False
    assert rule.check({"unit_price": "100"}) is False


def test_qty_positive_rule():
    rule = QtyPositiveRule()
    assert rule.check({"qty": 5}) is True
    assert rule.check({"qty": 0}) is False
    assert rule.check({"qty": -3}) is False
    assert rule.check({"qty": None}) is False


def test_discount_range_rule():
    rule = DiscountRangeRule()
    assert rule.check({"discount_pct": 0}) is True
    assert rule.check({"discount_pct": 50}) is True
    assert rule.check({"discount_pct": 100}) is True
    assert rule.check({"discount_pct": -10}) is False
    assert rule.check({"discount_pct": 150}) is False
    assert rule.check({}) is True


def test_return_after_sale_rule():
    rule = ReturnAfterSaleRule()
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    assert rule.check({"sale_datetime": yesterday, "return_date": now}) is True
    assert rule.check({"sale_datetime": now, "return_date": yesterday}) is False
    assert rule.check({"sale_datetime": now}) is True


def test_sku_exists_rule():
    rule = SkuExistsRule()
    assert rule.check({"catalog_price": 15000}) is True
    assert rule.check({"in_catalog": True}) is True
    assert rule.check({}) is False


def test_price_deviation_rule():
    # P-15: max_factor=1.5 → 50% farq gacha OK
    rule = PriceDeviationRule(max_factor=1.5)
    assert rule.check({"unit_price": 100, "catalog_price": 100}) is True
    assert rule.check({"unit_price": 140, "catalog_price": 100}) is True
    assert rule.check({"unit_price": 200, "catalog_price": 100}) is False
    assert rule.check({"unit_price": 100, "catalog_price": 0}) is True


def test_cashier_store_rule():
    rule = CashierStoreRule()
    assert rule.check({"store_code": "ST-001", "cashier_store_code": "ST-001"}) is True
    assert rule.check({"store_code": "ST-001", "cashier_store_code": "ST-002"}) is False
    assert rule.check({"store_code": "ST-001"}) is True  # enrich yo'q
