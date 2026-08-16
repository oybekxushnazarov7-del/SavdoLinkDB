from datetime import datetime
import logging
from pathlib import Path
import shutil
from typing import Any, Dict, Optional

from src.load.db import DatabaseConnection
from src.load.load_log import LoadLogger
from src.load.loaders import StagingLoader

logger = logging.getLogger(__name__)


class ETLPipeline:
    """Barcha ETL bosqichlarini birlashtiruvchi markaziy klass[cite: 1]."""

    def __init__(self, config: Dict[str, Any], extractor=None, validator=None) -> None:
        self.config = config
        self.extractor = extractor
        self.validator = validator

    def run(self, stage: str = "all", file_path: Optional[str] = None, dry_run: bool = False) -> Dict[str, Any]:
        """ETL ishini bajaradi va statistika qaytaradi[cite: 1]."""
        load_id = f"LOAD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        stats = {"rows_read": 0, "rows_valid": 0, "rows_rejected": 0, "rows_loaded": 0}

        target_file = Path(file_path) if file_path else Path(self.config.get("input_dir", "data/raw"))
        files = [target_file] if target_file.is_file() else list(target_file.glob("*.*"))

        with DatabaseConnection(self.config["db"]) as cursor:
            load_logger = LoadLogger(cursor)
            staging_loader = StagingLoader(cursor, self.config, load_id)

            for f in files:
                if load_logger.is_already_loaded(f.name):
                    logger.info(f"{f.name} ilgari yuklangan, o'tkazib yuborildi.")
                    continue

                log_id = load_logger.start(load_id, f.name)
                try:
                    # 1. Extract
                    records = self._extract(f)
                    stats["rows_read"] += len(records)

                    # 2. Transform
                    transformed = self._transform(records)

                    # 3. Validate
                    valid, rejected = self._validate(transformed)
                    stats["rows_valid"] += len(valid)
                    stats["rows_rejected"] += len(rejected)

                    # 4. Load (agar dry_run bo'lmasa)
                    if not dry_run and stage in ["all", "load"]:
                        loaded_cnt = staging_loader.load_sales(valid, f.name)
                        stats["rows_loaded"] += loaded_cnt

                    load_logger.finish(log_id, stats)

                except Exception as e:
                    load_logger.fail(log_id, str(e))
                    raise e

            if dry_run:
                # Dry run rejimida tranzaksiya ataylab bekor qilinadi
                cursor.connection.rollback()
                logger.info("Dry-run rejimi: O'zgarishlar DB ga saqlanmadi (Rollback).")

        # 5. Fayllarni faqat muvaffaqiyatli Commit'dan KEYIN arxivlaymiz[cite: 1]
        if not dry_run and stage == "all":
            for f in files:
                self._archive(f)

        return stats

    def _extract(self, path: Path):
        return self.extractor.extract(path) if self.extractor else []

    def _transform(self, batch):
        return batch

    def _validate(self, batch):
        if self.validator:
            return self.validator.validate_batch(batch)
        return batch, []

    def _archive(self, path: Path) -> None:
        """Muvaffaqiyatli yuklangan faylni archive qatlamiga o'tkazadi[cite: 1]."""
        archive_dir = Path(self.config.get("archive_dir", "data/archive"))
        archive_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(path), str(archive_dir / path.name))
        logger.info(f"{path.name} arxivga ko'chirildi[cite: 1].")