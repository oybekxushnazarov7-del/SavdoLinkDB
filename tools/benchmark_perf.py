"""S7: indeksli/indekssiz so'rov va INSERT narxini o'lchash."""
import argparse
import statistics
import time
from pathlib import Path

from src.config import load_settings, Config
from src.load.db import DatabaseConnection

QUERIES = {
    "q01": Path("sql/queries/q01_query.sql"),
    "q05": Path("sql/queries/q05_query.sql"),
    "q09": Path("sql/queries/q09_query.sql"),
}

INDEXES = [
    "IX_SalesHeader_SaleDate",
    "IX_SalesHeader_StoreId",
    "IX_SalesDetail_HeaderId",
    "IX_SalesDetail_ProductId",
    "IX_Product_CategoryId",
    "IX_Employee_StoreId",
    "IX_Returns_HeaderId",
    "IX_ProductPrice_Lookup",
]


def read_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run_timed(cursor, sql: str, repeats: int = 3) -> dict:
    times = []
    for _ in range(repeats):
        cursor.execute("SET STATISTICS IO, TIME ON")
        start = time.perf_counter()
        cursor.execute(sql)
        while cursor.nextset():
            pass
        elapsed_ms = (time.perf_counter() - start) * 1000
        times.append(elapsed_ms)
    return {"avg_ms": round(statistics.mean(times), 1), "runs": repeats}


def drop_indexes(cursor):
    for name in INDEXES:
        cursor.execute(
            f"""
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = ? AND object_id = OBJECT_ID('core.SalesHeader'))
                DROP INDEX {name} ON core.SalesHeader;
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = ? AND object_id = OBJECT_ID('core.SalesDetail'))
                DROP INDEX {name} ON core.SalesDetail;
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = ? AND object_id = OBJECT_ID('core.Product'))
                DROP INDEX {name} ON core.Product;
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = ? AND object_id = OBJECT_ID('core.Employee'))
                DROP INDEX {name} ON core.Employee;
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = ? AND object_id = OBJECT_ID('core.Returns'))
                DROP INDEX {name} ON core.Returns;
            IF EXISTS (SELECT 1 FROM sys.indexes WHERE name = ? AND object_id = OBJECT_ID('core.ProductPrice'))
                DROP INDEX {name} ON core.ProductPrice;
            """,
            (name,) * 6,
        )


def main():
    parser = argparse.ArgumentParser(description="S7 benchmark — q01, q05, q09")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    config = Config(load_settings("config/settings.json"))
    with DatabaseConnection(config.get("db", {})) as conn:
        cur = conn.cursor
        print("=== Indeks bilan ===")
        for code, path in QUERIES.items():
            result = run_timed(cur, read_sql(path), args.repeats)
            print(f"{code}: {result['avg_ms']} ms (o'rtacha, {args.repeats} marta)")

        print("\nIndekslarni vaqtincha o'chirish uchun sql/ddl/06_indexes.sql ni qayta ishga tushiring.")
        conn.rollback()


if __name__ == "__main__":
    main()
