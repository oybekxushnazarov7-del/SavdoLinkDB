import argparse
import logging
from calendar import monthrange
from pathlib import Path

from src.pipeline import ETLPipeline
from src.validate.validator import Validator
from src.config import load_settings, Config
from src.load.db import DatabaseConnection
from src.report.builder import ReportBuilder
from src.utils.logger import get_logger
from src.utils.helpers import make_load_id

logger = logging.getLogger("SavdoLink")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="savdolink",
        description="SavdoLink ETL Pipeline — Ma'lumotlarni qayta ishlash va yuklash tizimi",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Batafsil log (DEBUG)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="ETL jarayonini ishga tushiradi")
    run_parser.add_argument(
        "--stage",
        choices=["all", "extract", "transform", "load", "core", "mart"],
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
    run_parser.add_argument(
        "--load-id",
        type=str,
        default=None,
        help="core/mart bosqichi uchun LoadId (masalan LOAD-20260828-120000)",
    )
    run_parser.add_argument(
        "--month",
        type=str,
        default=None,
        help="mart bosqichi uchun davr: YYYY-MM",
    )

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

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    base_dir = Path(__file__).resolve().parent
    load_data = load_settings(path=str(base_dir / "config" / "settings.json"))
    config = Config(load_data)

    if args.command == "run":
        rules_path = base_dir / "config" / "validation_rules.json"
        validator = Validator.from_config(str(rules_path))

        run_load_id = args.load_id or make_load_id()
        # B-13: fayl va konsolga log
        run_logger = get_logger("SavdoLink", run_load_id)
        run_logger.info(
            "ETL Pipeline ishga tushmoqda... (Stage: %s, Dry-run: %s)",
            args.stage,
            args.dry_run,
        )

        month = args.month or "2026-02"
        date_from, date_to = _month_range(month)

        pipeline = ETLPipeline(config, validator=validator)
        stats = pipeline.run(
            stage=args.stage,
            file_path=args.file,
            dry_run=args.dry_run,
            load_id=run_load_id,
            date_from=date_from,
            date_to=date_to,
        )
        run_logger.info("ETL yakunlandi. Statistika: %s", stats)

    elif args.command == "report":
        month = args.month or "2026-02"
        date_from, date_to = _month_range(month)
        db_cfg = config.get("db", {})
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
