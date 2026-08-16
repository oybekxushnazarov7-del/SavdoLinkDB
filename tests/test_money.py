from decimal import Decimal
import pytest
from src.models.money import Money
from src.models.money import CurrencyMismatchError


def test_money_addition():
    m1 = Money(Decimal("100"), "UZS")
    m2 = Money(Decimal("50"), "UZS")
    assert m1 + m2 == Money(Decimal("150"), "UZS")


def test_money_subtraction():
    m1 = Money(Decimal("100"), "UZS")
    m2 = Money(Decimal("30"), "UZS")
    assert m1 - m2 == Money(Decimal("70"), "UZS")


def test_money_multiplication():
    m = Money(Decimal("100"), "UZS")
    assert m * 2 == Money(Decimal("200"), "UZS")


def test_money_add_different_currency():
    a = Money(Decimal("100"), "UZS")
    b = Money(Decimal("100"), "USD")
    with pytest.raises(CurrencyMismatchError):
        _ = a + b


def test_money_equality_and_hash():
    m1 = Money(Decimal("100"), "UZS")
    m2 = Money(Decimal("100"), "UZS")
    assert m1 == m2
    assert hash(m1) == hash(m2)