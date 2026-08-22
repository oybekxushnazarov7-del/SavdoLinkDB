"""
Fayl: tests/test_rules.py
Vazifasi: src/validate/rules.py modulidagi biznes va validatsiya qoidalarini sinash.
"""
from datetime import datetime, timedelta
import pytest

from src.validate.rules import (
    DateRequiredRule,
    DiscountRangeRule,
    PriceDeviationRule,
    PriceIsNumericRule,
    QtyIsIntRule,
    QtyPositiveRule,
    ReturnAfterSaleRule,
    SkuExistsRule,
    SkuRequiredRule,
    ValidationRule,
)


def test_base_validation_rule_not_implemented():
    """Bazaviy ValidationRule check() funksiyasi chaqirilganda NotImplementedError berishi kerak."""

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


def test_date_required_rule():
    rule = DateRequiredRule()
    assert rule.check({"date": "2026-03-14"}) is True
    assert rule.check({"date": None}) is False
    assert rule.check({}) is False


def test_qty_is_int_rule():
    rule = QtyIsIntRule()
    assert rule.check({"qty": 10}) is True
    assert rule.check({"qty": "10"}) is False
    assert rule.check({"qty": 10.5}) is False


def test_price_is_numeric_rule():
    rule = PriceIsNumericRule()
    assert rule.check({"price": 100}) is True
    assert rule.check({"price": 99.99}) is True
    assert rule.check({"price": True}) is False  # Bool tekshiruvi
    assert rule.check({"price": "100"}) is False


def test_qty_positive_rule():
    rule = QtyPositiveRule()
    assert rule.check({"qty": 5}) is True
    assert rule.check({"qty": 0}) is False
    assert rule.check({"qty": -3}) is False
    assert rule.check({"qty": None}) is False


def test_discount_range_rule():
    rule = DiscountRangeRule()
    assert rule.check({"discount": 0}) is True
    assert rule.check({"discount": 50}) is True
    assert rule.check({"discount": 100}) is True
    assert rule.check({"discount": -10}) is False
    assert rule.check({"discount": 150}) is False
    assert rule.check({}) is True  # Chegirma ko'rsatilmanganda True qaytadi


def test_return_after_sale_rule():
    rule = ReturnAfterSaleRule()
    now = datetime.now()
    yesterday = now - timedelta(days=1)

    assert rule.check({"sale_date": yesterday, "return_date": now}) is True
    assert rule.check({"sale_date": now, "return_date": yesterday}) is False
    assert rule.check({"sale_date": now}) is True  # Ikkala sana bo'lmasa True


def test_sku_exists_rule():
    rule = SkuExistsRule()
    assert rule.check({"catalog_price": 15000}) is True
    assert rule.check({"in_catalog": True}) is True
    assert rule.check({}) is False


def test_price_deviation_rule():
    rule = PriceDeviationRule()
    assert rule.check({"price": 100, "catalog_price": 100}) is True
    assert rule.check({"price": 140, "catalog_price": 100}) is True  # 40% farq (<= 50%)
    assert rule.check({"price": 200, "catalog_price": 100}) is False  # 100% farq (> 50%)
    assert rule.check({"price": 100, "catalog_price": 0}) is True  # Bo'lishda 0 bo'lsa True