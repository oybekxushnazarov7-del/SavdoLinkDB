from pathlib import Path
import logging
from typing import Any, Dict, Optional

from src.config import Config
from src.extract.factory import get_extractor
from src.validate.validator import Validator
from src.load.loaders import StagingLoader, REF_MAP
from src.load.db import DatabaseConnection
from src.load.load_log import LoadLogger
from src.validate.rejected_writer import RejectedWriter
from src.transform.parsers import parse_datetime, parse_decimal, parse_int
from src.transform.cleaners import clean_row, normalize_code, normalize_text, empty_to_none
from src.transform.deduplicator import deduplicate
from src.models.sale import SaleRecord
from src.validate.rules import DEFAULT_RULES
from src.utils.helpers import make_load_id, archive_file

logger = logging.getLogger("SavdoLink.Pipeline")

SALES_SPEC = {
    "sku": normalize_code,
    "store_code": normalize_code,
    "payment_type": normalize_code,
    "receipt_no": normalize_text,
}


def _transform_sale(row: dict) -> dict:
    # P-11: transform bosqichi — normalize → parse (validate dan OLDIN)
    """Xom qatorni tipli qiymatlarga aylantiradi. Qaror qabul qilmaydi."""
    out = clean_row(row, SALES_SPEC)
    out["qty"] = parse_int(empty_to_none(row.get("qty")))
    out["unit_price"] = parse_decimal(empty_to_none(row.get("unit_price")))
    out["discount_pct"] = parse_decimal(empty_to_none(row.get("discount_pct")))
    out["sale_datetime"] = parse_datetime(row.get("sale_datetime"))
    out["_raw"] = row  # stg uchun asl matn (S-05)
    out["_source_file"] = row.get("_source_file")
    out["_row_num"] = row.get("_row_num")
    return out


def to_sale_record(row: dict) -> SaleRecord:
    # P-16: domen modellari deduplicate uchun ishlatiladi (__hash__/__eq__)
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


class ETLPipeline:
    def __init__(
        self,
        config: Config,
        validator: Optional[Validator] = None,
    ):
        # P-07/P-08: loader va extractor __init__ da YARATILMAYDI
        self.config = config
        self.input_dir = Path(config.get("paths.incoming", "data/incoming"))
        self.archive_dir = Path(config.get("paths.archive", "data/archive"))
        self.validator = validator or Validator(DEFAULT_RULES)

    def run(
        self,
        stage: str = "all",
        file_path: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, int]:
        # P-17: LoadId + RejectedWriter + LoadLogger ulangan
        load_id = make_load_id()
        stats = {
            "rows_read": 0,
            "rows_valid": 0,
            "rows_rejected": 0,
            "rows_loaded": 0,
            "rows_duplicate": 0,
        }

        files_to_process = []
        if file_path:
            files_to_process.append(Path(file_path))
        elif self.input_dir.exists():
            files_to_process = sorted(
                f for f in self.input_dir.iterdir() if f.is_file()
            )

        if not files_to_process:
            logger.warning("Qayta ishlash uchun hech qanday fayl topilmadi.")
            return stats

        db_config = self.config.get("db", {})
        rejected_dir = Path(self.config.get("paths.rejected", "data/rejected"))
        rejected_path = rejected_dir / f"rejected_{load_id}.csv"

        # P-18: arxivlash COMMIT dan KEYIN — avval ro'yxatga yig'iladi
        archived = []

        with DatabaseConnection(db_config) as conn:
            # P-07: StagingLoader ulanish ochilgandan keyin
            loader = StagingLoader(conn.cursor, self.config, load_id)
            load_logger = LoadLogger(conn.cursor)

            with RejectedWriter(rejected_path, load_id) as rejected:
                for current_file in files_to_process:
                    # P-09: idempotentlik
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
                        "rows_loaded": 0,
                    }

                    try:
                        valid_data = []
                        if stage in ["all", "extract", "transform"]:
                            # P-05/P-08: har fayl uchun get_extractor + read()
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
                                        r for r in transformed_rows
                                        if r.get("_row_num") in unique_row_nums
                                    ]

                                for row in transformed_rows:
                                    # Sales bo'lmagan spravochniklarga qattiq sales qoidalari
                                    # qo'llanmasin — faqat sales_* validate qilinadi
                                    if is_sales:
                                        validation_result = self.validator.validate(row)
                                        if validation_result.is_valid:
                                            valid_data.append(row)
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
                            # P-06: umumiy load() yo'q — fayl turiga qarab metod
                            name = current_file.name.lower()
                            stem = current_file.stem.lower()
                            if name.startswith("sales_"):
                                loaded_count = loader.load_sales(valid_data, current_file.name)
                            elif name.startswith("products"):
                                loaded_count = loader.load_products(valid_data, current_file.name)
                                # products.json price_history → stg.RawPrices
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
                                logger.warning("Noma'lum fayl turi, o'tkazib yuborildi: %s", name)
                                loaded_count = 0

                            file_stats["rows_loaded"] += loaded_count or 0

                        if stage == "all" and current_file.exists():
                            archived.append(current_file)

                        load_logger.finish(log_id, file_stats, "SUCCESS")

                        for k, v in file_stats.items():
                            stats[k] += v

                    except Exception as exc:
                        load_logger.fail(log_id, str(exc))
                        raise

            if dry_run:
                conn.rollback()
                logger.info("Dry-run: o'zgarishlar bekor qilindi")
                archived.clear()  # rollback bo'lsa arxivlamaymiz

        # P-18: COMMIT (yoki dry-run rollback) dan keyin arxivlash
        if not dry_run and stage == "all":
            self.archive_dir.mkdir(parents=True, exist_ok=True)
            for f in archived:
                if f.exists():
                    archive_file(f, self.archive_dir)
                    logger.info("Fayl arxivga ko'chirildi: %s", self.archive_dir / f.name)

        logger.info("Yakun: %s", stats)
        return stats
