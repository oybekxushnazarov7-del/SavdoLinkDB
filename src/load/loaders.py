import logging
from typing import Any, Dict, Iterable, List, Sequence, Union

logger = logging.getLogger(__name__)

# S-06: faqat haqiqiy stg jadvallar (RawCashiers yo'q).
STAGING_TABLES = [
    "stg.RawSales",
    "stg.RawProducts",
    "stg.RawPrices",
    "stg.RawStores",
    "stg.RawEmployees",
    "stg.RawCategories",
    "stg.RawSuppliers",
    "stg.RawReturns",
    "stg.RawRates",
]

# Reference fayl stem → (stg jadval, snake_case → PascalCase xarita)
REF_MAP = {
    "stores": (
        "stg.RawStores",
        {
            "store_code": "StoreCode",
            "store_name": "StoreName",
            "region": "Region",
            "city": "City",
            "opened_date": "OpenedDate",
            "area_m2": "AreaM2",
        },
    ),
    "employees": (
        "stg.RawEmployees",
        {
            "emp_id": "EmpCode",
            "full_name": "FullName",
            "store_code": "StoreCode",
            "position": "Position",
            "salary": "Salary",
            "hired_date": "HiredDate",
            "manager_id": "ManagerCode",
            "is_active": "IsActive",
        },
    ),
    "categories": (
        "stg.RawCategories",
        {
            "category_code": "CategoryCode",
            "name": "CategoryName",
            "parent_code": "ParentCategoryCode",
            "level": "Level",
        },
    ),
    "suppliers": (
        "stg.RawSuppliers",
        {
            "inn": "Inn",
            "supplier_name": "SupplierName",
            "country": "Country",
            "contract_date": "ContractDate",
        },
    ),
    "returns": (
        "stg.RawReturns",
        {
            "return_id": "ReturnId",
            "receipt_no": "ReceiptNo",
            "store_code": "StoreCode",
            "sku": "Sku",
            "qty": "Qty",
            "reason": "Reason",
            "return_date": "ReturnDate",
        },
    ),
    "exchange_rates": (
        "stg.RawRates",
        {
            "rate_date": "RateDate",
            "currency_code": "CurrencyCode",
            "rate": "Rate",
        },
    ),
}


class BulkLoader:
    """Qatorlarni paket-paket qilib executemany orqali tezkor yozuvchi sinf."""

    def __init__(self, cursor, table: str, columns: Sequence[str], batch_size: int = 1000) -> None:
        self.cursor = cursor
        self.table = table
        self.columns = columns
        self.batch_size = batch_size
        self.buffer: List[Union[tuple, dict]] = []
        self._total_loaded = 0

        placeholders = ", ".join(["?"] * len(columns))
        col_list = ", ".join(columns)
        self.sql = f"INSERT INTO {table} ({col_list}) VALUES ({placeholders})"

    def add(self, row: Union[tuple, dict]) -> None:
        """Buferga qator qo'shadi, chegaraga yetsa avtomatik flush qiladi."""
        self.buffer.append(row)
        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> int:
        """Buferni DB ga yozib tozalaydi."""
        if not self.buffer:
            return 0
        logger.debug("SQL: %s", self.sql)
        self.cursor.executemany(self.sql, self.buffer)
        written = len(self.buffer)
        self._total_loaded += written
        self.buffer.clear()
        return written

    def close(self) -> int:
        """Qolib ketgan qatorlarni yozadi va jami sonini qaytaradi."""
        self.flush()
        return self._total_loaded

    @property
    def total_loaded(self) -> int:
        return self._total_loaded

    def __enter__(self) -> "BulkLoader":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()


class StagingLoader:
    """stg jadvallariga xizmat ustunlari (LoadId, SourceFile, RowNum) bilan yozuvchi sinf."""

    def __init__(self, cursor, cfg, load_id: str) -> None:
        self.cursor = cursor
        self.cfg = cfg
        self.load_id = load_id

    def _batch_size(self) -> int:
        # Config obyekti yoki oddiy dict bo'lishi mumkin
        if hasattr(self.cfg, "get"):
            val = self.cfg.get("load.batch_size", 1000)
            if val is not None:
                return int(val)
        return 1000

    def load_sales(self, records: Iterable[Dict[str, Any]], source_file: str) -> int:
        # S-05: loaders.py eski SaleId/StoreId yozgan — stg.RawSales da ReceiptNo/StoreCode/...
        """stg.RawSales jadvaliga ASL matn (_raw) bilan yozadi."""
        columns = [
            "LoadId", "SourceFile", "RowNum",
            "ReceiptNo", "StoreCode", "CashierId", "SaleDateTime",
            "Sku", "Qty", "UnitPrice", "DiscountPct", "PaymentType",
            "UnitPriceResolved", "PriceSource",
        ]
        loader = BulkLoader(
            self.cursor, "stg.RawSales", columns, batch_size=self._batch_size()
        )
        for rec in records:
            raw = rec.get("_raw", rec)  # stg ga asl matn
            loader.add((
                self.load_id,
                source_file,
                rec.get("_row_num", 0),  # enumerate emas — rad etilganlar siljitmasin
                raw.get("receipt_no"),
                raw.get("store_code"),
                raw.get("cashier_id"),
                raw.get("sale_datetime"),
                raw.get("sku"),
                raw.get("qty"),
                raw.get("unit_price"),
                raw.get("discount_pct"),
                raw.get("payment_type"),
                str(rec.get("unit_price")) if rec.get("unit_price") is not None else None,
                rec.get("_price_source", "file"),
            ))
        return loader.close()

    def load_products(self, records: Iterable[Dict[str, Any]], source_file: str) -> int:
        # S-05 / RawProducts DDL: Sku, ProductName, CategoryCode, SupplierInn, Unit, Barcode, IsActive
        """stg.RawProducts jadvaliga yozadi."""
        columns = [
            "LoadId", "SourceFile", "RowNum",
            "Sku", "ProductName", "CategoryCode", "SupplierInn",
            "Unit", "Barcode", "IsActive",
        ]
        loader = BulkLoader(
            self.cursor, "stg.RawProducts", columns, batch_size=self._batch_size()
        )
        for rec in records:
            raw = rec.get("_raw", rec)
            loader.add((
                self.load_id,
                source_file,
                rec.get("_row_num", 0),
                raw.get("sku"),
                raw.get("name") or raw.get("product_name"),
                raw.get("category_code"),
                raw.get("supplier_inn"),
                raw.get("unit"),
                raw.get("barcode"),
                raw.get("is_active"),
            ))
        return loader.close()

    def load_prices(self, records: Iterable[Dict[str, Any]], source_file: str) -> int:
        """stg.RawPrices — products.json dagi price_history yassilangan qatorlari."""
        columns = ["LoadId", "SourceFile", "RowNum", "Sku", "ValidFrom", "ValidTo", "Price"]
        loader = BulkLoader(
            self.cursor, "stg.RawPrices", columns, batch_size=self._batch_size()
        )
        for rec in records:
            loader.add((
                self.load_id,
                source_file,
                rec.get("_row_num", 0),
                rec.get("sku"),
                rec.get("valid_from"),
                rec.get("valid_to"),
                rec.get("price"),
            ))
        return loader.close()

    def load_reference(self, table_key: str, records: Iterable[Dict[str, Any]], source_file: str) -> int:
        """Spravochniklar: stem bo'yicha stg jadval va ustun xaritasini tanlaydi."""
        if table_key not in REF_MAP:
            logger.warning("Noma'lum reference jadval: %s", table_key)
            return 0

        table, field_map = REF_MAP[table_key]
        records_list = list(records)
        if not records_list:
            return 0

        data_cols = list(field_map.values())
        all_columns = ["LoadId", "SourceFile", "RowNum"] + data_cols
        loader = BulkLoader(
            self.cursor, table, all_columns, batch_size=self._batch_size()
        )

        for rec in records_list:
            raw = rec.get("_raw", rec)
            values = []
            for src_key in field_map:
                val = raw.get(src_key)
                # JSON bool/None ni matnga yaqinlashtirish
                if isinstance(val, bool):
                    val = "1" if val else "0"
                values.append(val)
            loader.add(
                (self.load_id, source_file, rec.get("_row_num", 0)) + tuple(values)
            )

        return loader.close()

    def truncate_staging(self, load_id: str = None) -> None:
        # S-06: try/except yashirish o'rniga aniq jadvallar; LoadId bo'yicha DELETE.
        """Staging jadvallarini tozalaydi (LoadId bo'lsa faqat shu yuklash)."""
        for tbl in STAGING_TABLES:
            if load_id:
                self.cursor.execute(f"DELETE FROM {tbl} WHERE LoadId = ?", (load_id,))
            else:
                self.cursor.execute(f"TRUNCATE TABLE {tbl}")
        logger.info("Staging jadvallari tozalandi.")
