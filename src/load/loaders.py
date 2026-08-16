import logging
from typing import Any, Dict, Iterable, List, Sequence, Union

logger = logging.getLogger(__name__)


class BulkLoader:
    """Qatorlarni paket-paket qilib executemany orqali tezkor yozuvchi sinf[cite: 1]."""

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
        """Buferga qator qo'shadi, chegaraga yetsa avtomatik flush qiladi[cite: 1]."""
        self.buffer.append(row)
        if len(self.buffer) >= self.batch_size:
            self.flush()

    def flush(self) -> int:
        """Buferni DB ga yozib tozalaydi[cite: 1]."""
        if not self.buffer:
            return 0
        self.cursor.executemany(self.sql, self.buffer)
        written = len(self.buffer)
        self._total_loaded += written
        self.buffer.clear()
        return written

    def close(self) -> int:
        """Qolib ketgan qatorlarni yozadi va jami sonini qaytaradi[cite: 1]."""
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
    """stg jadvallariga xizmat ustunlari (LoadId, SourceFile, RowNum) bilan yozuvchi sinf[cite: 1]."""

    def __init__(self, cursor, cfg: dict, load_id: str) -> None:
        self.cursor = cursor
        self.cfg = cfg
        self.load_id = load_id

    def load_sales(self, records: Iterable[Dict[str, Any]], source_file: str) -> int:
        """stg.RawSales jadvaliga yozadi[cite: 1]."""
        columns = [
            "LoadId", "SourceFile", "RowNum",
            "SaleId", "SaleDate", "StoreId", "CashierId", "TotalAmount", "PaymentMethod"
        ]
        loader = BulkLoader(self.cursor, "stg.RawSales", columns)
        for idx, rec in enumerate(records, start=1):
            row = (
                self.load_id, source_file, idx,
                rec.get("sale_id"), rec.get("sale_date"), rec.get("store_id"),
                rec.get("cashier_id"), rec.get("total_amount"), rec.get("payment_method")
            )
            loader.add(row)
        return loader.close()

    def load_products(self, records: Iterable[Dict[str, Any]], source_file: str) -> int:
        """stg.RawProducts jadvaliga yozadi[cite: 1]."""
        columns = [
            "LoadId", "SourceFile", "RowNum",
            "ProductId", "SKUKode", "ProductName", "Category", "Price"
        ]
        loader = BulkLoader(self.cursor, "stg.RawProducts", columns)
        for idx, rec in enumerate(records, start=1):
            row = (
                self.load_id, source_file, idx,
                rec.get("product_id"), rec.get("sku_code"),
                rec.get("product_name"), rec.get("category"), rec.get("price")
            )
            loader.add(row)
        return loader.close()

    def load_reference(self, table: str, records: Iterable[Dict[str, Any]], source_file: str) -> int:
        """Spravochniklar uchun umumiy dinamik yuklagich[cite: 1]."""
        records_list = list(records)
        if not records_list:
            return 0

        data_fields = list(records_list[0].keys())
        all_columns = ["LoadId", "SourceFile", "RowNum"] + data_fields
        loader = BulkLoader(self.cursor, table, all_columns)

        for idx, rec in enumerate(records_list, start=1):
            row = (self.load_id, source_file, idx) + tuple(rec.get(col) for col in data_fields)
            loader.add(row)

        return loader.close()

    def truncate_staging(self) -> None:
        """Staging jadvallarini tozalaydi[cite: 1]."""
        for tbl in ["stg.RawSales", "stg.RawProducts", "stg.RawStores", "stg.RawCashiers"]:
            try:
                self.cursor.execute(f"TRUNCATE TABLE {tbl}")
            except Exception:
                self.cursor.execute(f"DELETE FROM {tbl}")
        logger.info("Staging jadvallari tozalandi.")