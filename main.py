import argparse
import logging
from src.pipeline import ETLPipeline

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

    # 'run' buyrug'i
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

    subparsers.add_parser("init-db", help="Bazani va jadval strukturalarini tayyorlaydi")
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    config = {
        "db": {
            "driver": "ODBC Driver 17 for SQL Server",
            "server": "DESKTOP-EU0USCO\SQLEXPRESS",
            "database": "SavdoLinkDB",
            "trusted_connection": True,
        },
        "input_dir": "data/incoming",
        "archive_dir": "data/archive",
    }

    if args.command == "run":
        logger.info(f"ETL Pipeline ishga tushmoqda... (Stage: {args.stage}, Dry-run: {args.dry_run})")
        pipeline = ETLPipeline(config)
        stats = pipeline.run(stage=args.stage, file_path=args.file, dry_run=args.dry_run)
        logger.info(f"ETL yakunlandi. Statistika: {stats}")


if __name__ == "__main__":
    main()