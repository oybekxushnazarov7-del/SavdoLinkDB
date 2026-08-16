from datetime import date
from decimal import Decimal
from src.models.money import Money
from src.models.product import Product, PricePoint
from src.models.sale import SaleRecord
from src.models.batch import Batch


def test_product_price_at():
    p = Product(
        sku="SKU-001",
        name="Sut",
        category_code="CAT-1",
        supplier_inn="123456789",
        unit="dona",
        prices=[
            PricePoint(valid_from=date(2026, 1, 1), price=Money(Decimal("10000"), "UZS")),
            PricePoint(valid_from=date(2026, 6, 1), price=Money(Decimal("12000"), "UZS")),
        ],
    )
    assert p.price_at(date(2026, 3, 1)) == Money(Decimal("10000"), "UZS")
    assert p.price_at(date(2026, 7, 1)) == Money(Decimal("12000"), "UZS")
    assert p.price_at(date(2025, 12, 31)) is None


def test_sale_record_unique_key():
    sale = SaleRecord(
        receipt_no="REC-001",
        store_code="ST-01",
        cashier_id="C-01",
        sale_datetime_raw="2026-08-12",
        sku="SKU-001",
        qty_raw="2",
        unit_price_raw="10000",
        discount_raw="0",
        payment_type="CARD",
        source_file="sales.csv",
        row_num=2,
    )
    assert sale.unique_key() == ("REC-001", "SKU-001")


def test_batch_dunder_methods():
    batch = Batch()
    assert not batch  # __bool__
    
    batch.add("record_1")
    batch.add("record_2")
    
    assert len(batch) == 2  # __len__
    assert batch[0] == "record_1"  # __getitem__
    assert "record_1" in batch  # __contains__
    assert list(batch) == ["record_1", "record_2"]  # __iter__