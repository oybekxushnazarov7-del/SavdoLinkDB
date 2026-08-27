import argparse
import logging
from calendar import monthrange
from pathlib import Path

from src.pipeline import ETLPipeline
from src.validate.validator import Validator
from src.config import load_settings, Config
from src.validate.rules import DEFAULT_RULES
from src.load.db import DatabaseConnection
from src.report.builder import ReportBuilder

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("SavdoLink")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="savdolink",
        description="SavdoLink ETL Pipeline — Ma'lumotlarni qayta ishlash va yuklash tizimi",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="ETL jarayonini ishga tushiradi")
    run_parser.add_argument(
        "--stage",
        choices=["all", "extract", "transform", "load"],
        default="all",
        help="Bajariladigan ETL bosqichi (default: all)",
    )
    run_parser.add_argument(
        "--file",
        type=str,
        default=None,
        help="Muayyan bitta faylni qayta ishlash uchun yo'l",
    )
    run_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Bazaga saqlamasdan sinov rejimida ishga tushirish (Rollback)",
    )

    # Qadam 8: report CLI
    report_parser = subparsers.add_parser("report", help="HTML hisobot yasaydi")
    report_parser.add_argument(
        "--type",
        choices=["dashboard", "store", "dq", "load_log"],
        default="dashboard",
        help="Hisobot turi",
    )
    report_parser.add_argument(
        "--month",
        type=str,
        default=None,
        help="Davr: YYYY-MM (dashboard/store uchun)",
    )
    report_parser.add_argument("--store", type=str, default=None, help="Do'kon kodi")
    report_parser.add_argument("--load-id", type=str, default=None, help="DQ hisoboti uchun LoadId")

    subparsers.add_parser("init-db", help="Bazani va jadval strukturalarini tayyorlaydi")
    return parser


def _month_range(month: str):
    """YYYY-MM → (date_from, date_to)."""
    year, mon = map(int, month.split("-"))
    last = monthrange(year, mon)[1]
    return f"{year:04d}-{mon:02d}-01", f"{year:04d}-{mon:02d}-{last:02d}"


def main():
    parser = build_parser()
    args = parser.parse_args()

    # P-02: pathlib — Windows `\` f-string escape ogohlantirishisiz
    base_dir = Path(__file__).resolve().parent
    load_data = load_settings(path=str(base_dir / "config" / "settings.json"))
    config = Config(load_data)

    if args.command == "run":
        logger.info(
            "ETL Pipeline ishga tushmoqda... (Stage: %s, Dry-run: %s)",
            args.stage,
            args.dry_run,
        )
        # P-04: Validator(DEFAULT_RULES); P-08: extractor main da yaratilmaydi
        validator = Validator(DEFAULT_RULES)
        pipeline = ETLPipeline(config, validator=validator)
        stats = pipeline.run(stage=args.stage, file_path=args.file, dry_run=args.dry_run)
        logger.info("ETL yakunlandi. Statistika: %s", stats)

    elif args.command == "report":
        month = args.month or "2026-02"
        date_from, date_to = _month_range(month)
        db_cfg = config.get("db", {})
        # ReportBuilder cfg.paths kutadi — butun settings lug'ati
        with DatabaseConnection(db_cfg) as conn:
            builder = ReportBuilder(load_data, conn.cursor)
            if args.type == "dashboard":
                out = builder.build_dashboard(date_from, date_to)
            elif args.type == "store":
                if not args.store:
                    raise SystemExit("--store majburiy (masalan ST-001)")
                out = builder.build_store_report(args.store, date_from, date_to)
            elif args.type == "dq":
                if not args.load_id:
                    raise SystemExit("--load-id majburiy")
                out = builder.build_dq_report(args.load_id)
            else:
                out = builder.build_load_log()
            logger.info("Hisobot yozildi: %s", out)

    elif args.command == "init-db":
        logger.warning(
            "init-db: SQL skriptlarni qo'lda ishga tushiring "
            "(sql/ddl/00_database.sql … 06_indexes.sql). "
            "Avtomatik ijro hali ulanmagan."
        )


if __name__ == "__main__":
    main()
