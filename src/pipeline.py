from pathlib import Path
import logging
from typing import Any, Dict, List, Optional
import json

from src.config import Config
from src.extract.factory import get_extractor
from src.validate.validator import Validator
from src.load.loaders import StagingLoader, REF_MAP
from src.load.db import DatabaseConnection
from src.load.load_log import LoadLogger
from src.validate.rejected_writer import RejectedWriter
from src.validate.dq_report import build_report
from src.transform.parsers import parse_datetime, parse_decimal, parse_int
from src.transform.cleaners import clean_row, normalize_code, normalize_text, empty_to_none
from src.transform.deduplicator import deduplicate
from src.transform.enrichers import PriceCatalog, enrich_sale
from src.models.sale import SaleRecord
from src.validate.rules import DEFAULT_RULES, StoreExistsRule
from src.utils.helpers import make_load_id, archive_file, full_sales_date_range
from src.exceptions import ExtractError

logger = logging.getLogger("SavdoLink.Pipeline")

PROC_SOURCES = [
    (
        "core.usp_LoadDimensions",
        ("stg.RawStores", "stg.RawEmployees", "stg.RawCategories", "stg.RawSuppliers"),
    ),
    ("core.usp_LoadProducts", ("stg.RawProducts",)),
    ("core.usp_LoadSales", ("stg.RawSales",)),
    ("core.usp_LoadReturns", ("stg.RawReturns",)),
]

SALES_SPEC = {
    "sku": normalize_code,
    "store_code": normalize_code,
    "payment_type": normalize_code,
    "receipt_no": normalize_text,
}


def _transform_sale(row: dict) -> dict:
    """Xom qatorni tipli qiymatlarga aylantiradi. Qaror qabul qilmaydi."""
    out = clean_row(row, SALES_SPEC)
    out["qty"] = parse_int(empty_to_none(row.get("qty")))
    out["unit_price"] = parse_decimal(empty_to_none(row.get("unit_price")))
    out["discount_pct"] = parse_decimal(empty_to_none(row.get("discount_pct")))
    out["sale_datetime"] = parse_datetime(row.get("sale_datetime"))
    out["_raw"] = row
    out["_source_file"] = row.get("_source_file")
    out["_row_num"] = row.get("_row_num")
    return out


def to_sale_record(row: dict) -> SaleRecord:
    return SaleRecord(
        receipt_no=row.get("receipt_no"),
        store_code=row.get("store_code"),
        cashier_id=row.get("cashier_id"),
        sale_datetime_raw=row.get("sale_datetime", ""),
        sku=row.get("sku"),
        qty_raw=str(row.get("qty", "")),
        unit_price_raw=str(row.get("unit_price", "")),
        discount_raw=str(row.get("discount_pct", "")),
        payment_type=row.get("payment_type", ""),
        source_file=row.get("_source_file", ""),
        row_num=row.get("_row_num", 0),
    )


def _load_reference_dicts(input_dir: Path) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """stores va employees ma'lumotlarini CashierStoreRule uchun yig'adi."""
    stores: Dict[str, Any] = {}
    employees: Dict[str, Any] = {}

    stores_file = input_dir / "stores.csv"
    if stores_file.exists():
        for row in get_extractor(stores_file).read():
            code = row.get("store_code")
            if code:
                stores[str(code).strip()] = row

    employees_file = input_dir / "employees.json"
    if employees_file.exists():
        for row in get_extractor(employees_file).read():
            emp_id = row.get("emp_id")
            if emp_id:
                employees[str(emp_id).strip()] = row

    return stores, employees


def _build_price_catalog(input_dir: Path) -> Optional[PriceCatalog]:
    """products.json dan narx katalogini quradi."""
    products_file = input_dir / "products.json"
    if not products_file.exists():
        return None
    return PriceCatalog(list(get_extractor(products_file).read()))


class ETLPipeline:
    def __init__(
        self,
        config: Config,
        validator: Optional[Validator] = None,
    ):
        self.config = config
        self.input_dir = Path(config.get("paths.incoming", "data/incoming"))
        self.archive_dir = Path(config.get("paths.archive", "data/archive"))
        self.validator = validator or Validator(DEFAULT_RULES)

    def promote_to_core(self, conn, load_id: str) -> Dict[str, Any]:
        """stg → core: faqat manbasi bo'sh bo'lmagan protseduralarni chaqiradi."""
        cur = conn.cursor
        executed, skipped = [], []

        for proc, tables in PROC_SOURCES:
            total = 0
            for tbl in tables:
                cur.execute(f"SELECT COUNT(*) FROM {tbl} WHERE LoadId = ?", (load_id,))
                row = cur.fetchone()
                total += row[0] if row else 0

            if total == 0:
                logger.info("%s o'tkazib yuborildi — manbada qator yo'q", proc)
                skipped.append(proc)
                continue

            cur.execute(f"EXEC {proc} @LoadId = ?", (load_id,))
            logger.info("%s bajarildi [manbada %s qator]", proc, total)
            executed.append(proc)

        return {"load_id": load_id, "executed": executed, "skipped": skipped}

    def promote_to_mart(self, conn, date_from: str, date_to: str) -> Dict[str, str]:
        """core → mart: kunlik faktlarni yangilaydi."""
        cur = conn.cursor
        cur.execute(
            "EXEC mart.usp_RefreshDailyFacts @DateFrom = ?, @DateTo = ?",
            (date_from, date_to),
        )
        logger.info(
            "mart.usp_RefreshDailyFacts bajarildi [%s — %s]", date_from, date_to
        )
        return {"date_from": date_from, "date_to": date_to, "status": "mart_refreshed"}

    def run(
        self,
        stage: str = "all",
        file_path: Optional[str] = None,
        dry_run: bool = False,
        load_id: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
    ) -> Dict[str, int]:
        load_id = load_id or make_load_id()
        stats: Dict[str, int] = {
            "rows_read": 0,
            "rows_valid": 0,
            "rows_rejected": 0,
            "db_rows_written": 0,
            "rows_duplicate": 0,
            "files_failed": 0,
        }
        all_valid_sales: List[dict] = []

        db_config = self.config.get("db", {})

        if stage in ("core", "mart"):
            with DatabaseConnection(db_config) as conn:
                if stage == "core":
                    self.promote_to_core(conn, load_id)
                else:
                    if not date_from or not date_to:
                        raise ValueError("mart bosqichi uchun date_from va date_to kerak")
                    self.promote_to_mart(conn, date_from, date_to)
                if dry_run:
                    conn.rollback()
            return stats

        files_to_process: List[Path] = []
        if file_path:
            files_to_process.append(Path(file_path))
        elif self.input_dir.exists():
            files_to_process = sorted(
                f for f in self.input_dir.iterdir() if f.is_file()
            )

        if not files_to_process:
            logger.warning("Qayta ishlash uchun hech qanday fayl topilmadi.")
            return stats

        rejected_dir = Path(self.config.get("paths.rejected", "data/rejected"))
        rejected_path = rejected_dir / f"rejected_{load_id}.csv"
        archived: List[Path] = []

        # B-05: katalog va spravochniklar sikldan oldin
        catalog = _build_price_catalog(self.input_dir)
        stores, employees = _load_reference_dicts(self.input_dir)

        store_codes = {
            str(code).strip().upper()
            for code in stores
            if code
        }
        for rule in self.validator.rules:
            if isinstance(rule, StoreExistsRule):
                rule.known_stores = store_codes

        with DatabaseConnection(db_config) as conn:
            loader = StagingLoader(conn.cursor, self.config, load_id)
            load_logger = LoadLogger(conn.cursor)

            if stage in ("all", "load"):
                loader.truncate_staging(load_id=load_id)

            with RejectedWriter(rejected_path, load_id) as rejected:
                for current_file in files_to_process:
                    if load_logger.is_already_loaded(current_file.name):
                        logger.info(
                            "Fayl ilgari yuklangan, o'tkazib yuborildi: %s",
                            current_file.name,
                        )
                        continue

                    logger.info("Fayl qayta ishlanmoqda: %s", current_file.name)
                    log_id = load_logger.start(load_id, current_file.name)

                    file_stats = {
                        "rows_read": 0,
                        "rows_valid": 0,
                        "rows_rejected": 0,
                        "db_rows_written": 0,
                    }

                    try:
                        valid_data: List[dict] = []
                        if stage in ["all", "extract", "transform"]:
                            extractor = get_extractor(current_file)

                            raw_rows = []
                            for row in extractor.read():
                                file_stats["rows_read"] += 1
                                raw_rows.append(row)

                            transformed_rows = []
                            if stage in ["all", "transform"]:
                                is_sales = current_file.name.startswith("sales_")
                                for row in raw_rows:
                                    if is_sales:
                                        t_row = _transform_sale(row)
                                        if catalog:
                                            t_row = enrich_sale(
                                                t_row, catalog, stores, employees
                                            )
                                    else:
                                        t_row = dict(row)
                                        t_row["_raw"] = row
                                    transformed_rows.append(t_row)

                                if is_sales:
                                    records = [to_sale_record(r) for r in transformed_rows]
                                    unique_records, duplicate_records = deduplicate(
                                        records, key_func=lambda r: r.unique_key()
                                    )
                                    stats["rows_duplicate"] += len(duplicate_records)
                                    unique_row_nums = {r.row_num for r in unique_records}
                                    transformed_rows = [
                                        r
                                        for r in transformed_rows
                                        if r.get("_row_num") in unique_row_nums
                                    ]

                                for row in transformed_rows:
                                    if is_sales:
                                        validation_result = self.validator.validate(row)
                                        if validation_result.is_valid:
                                            valid_data.append(row)
                                            all_valid_sales.append(row)
                                            file_stats["rows_valid"] += 1
                                        else:
                                            file_stats["rows_rejected"] += 1
                                            rejected.write(
                                                validation_result,
                                                current_file.name,
                                                row.get("_row_num"),
                                            )
                                    else:
                                        valid_data.append(row)
                                        file_stats["rows_valid"] += 1
                            else:
                                valid_data = raw_rows

                        if stage in ["all", "load"] and valid_data:
                            name = current_file.name.lower()
                            stem = current_file.stem.lower()
                            if name.startswith("sales_"):
                                loaded_count = loader.load_sales(
                                    valid_data, current_file.name
                                )
                            elif name.startswith("products"):
                                loaded_count = loader.load_products(
                                    valid_data, current_file.name
                                )
                                if name.endswith(".json"):
                                    price_rows = []
                                    for prod in valid_data:
                                        raw = prod.get("_raw", prod)
                                        for ph in raw.get("price_history") or []:
                                            price_rows.append({
                                                "sku": raw.get("sku"),
                                                "valid_from": ph.get("valid_from"),
                                                "valid_to": ph.get("valid_to"),
                                                "price": ph.get("price"),
                                                "_row_num": prod.get("_row_num", 0),
                                            })
                                    if price_rows:
                                        loaded_count += loader.load_prices(
                                            price_rows, current_file.name
                                        )
                            elif stem in REF_MAP:
                                loaded_count = loader.load_reference(
                                    stem, valid_data, current_file.name
                                )
                            else:
                                logger.warning(
                                    "Noma'lum fayl turi, o'tkazib yuborildi: %s", name
                                )
                                loaded_count = 0

                            file_stats["db_rows_written"] += loaded_count or 0

                        if stage == "all" and current_file.exists():
                            archived.append(current_file)

                        load_logger.finish(log_id, file_stats, "SUCCESS")

                        for k in ("rows_read", "rows_valid", "rows_rejected", "db_rows_written"):
                            stats[k] += file_stats[k]

                    except (ExtractError, json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
                        # KUTILGAN xato: fayl buzuq. Qayd etamiz va KEYINGISIGA o'tamiz.
                        load_logger.fail(log_id, f"Fayl o'qilmadi: {exc}")
                        stats["files_failed"] = stats.get("files_failed", 0) + 1
                        logger.error("Fayl o'tkazib yuborildi: %s — %s", current_file.name, exc)
                        continue

                    except Exception as exc:
                        # KUTILMAGAN xato: kod nosozligi. Tizimni to'xtatamiz.
                        load_logger.fail(log_id, str(exc))
                        raise

            if dry_run:
                conn.rollback()
                logger.info("Dry-run: o'zgarishlar bekor qilindi")
                archived.clear()

        if not dry_run and stage == "all":
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            for f in archived:
                if f.exists():
                    archive_file(f, self.archive_dir)
                    logger.info("Fayl arxivga ko'chirildi: %s", self.archive_dir / f.name)

        # B-09: balans tekshiruvi
        balance = (
            stats["rows_valid"] + stats["rows_rejected"] + stats["rows_duplicate"]
        )
        ok = balance == stats["rows_read"]
        logger.info(
            "Balans: %s = %s %s",
            stats["rows_read"],
            balance,
            "✓" if ok else "✗ YOZUV YO'QOLDI",
        )

        # B-06: DQ hisoboti
        if all_valid_sales:
            dq = build_report(
                records=all_valid_sales,
                rejected_count=stats["rows_rejected"],
                required_fields=[
                    "receipt_no",
                    "store_code",
                    "sku",
                    "qty",
                    "unit_price",
                ],
                key_func=lambda r: (r.get("receipt_no"), r.get("sku")),
                catalog=catalog or PriceCatalog([]),
                thresholds=self.config.get("quality", {}),
            )
            logger.info("DQ: %s", dq["metrics"])
            logger.info("Qoidalar statistikasi: %s", self.validator.stats)

        if stats["files_failed"]:
            logger.warning("DIQQAT: %s ta fayl qayta ishlanmadi", stats["files_failed"])

        if stage == "all" and not dry_run:
            with DatabaseConnection(db_config) as conn:
                self.promote_to_core(conn, load_id)
                mart_from, mart_to = date_from, date_to
                if not mart_from or not mart_to:
                    mart_from, mart_to = full_sales_date_range(conn.cursor)
                self.promote_to_mart(conn, mart_from, mart_to)

        logger.info("Yakun: %s", stats)
        return stats
