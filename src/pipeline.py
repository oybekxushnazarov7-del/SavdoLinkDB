from pathlib import Path
import logging
from typing import Any, Dict, Optional

from src.config import Config
from src.extract.factory import get_extractor
from src.extract.csv_extractor import CsvExtractor
from src.validate.validator import Validator
from src.load.loaders import StagingLoader
from src.load.db import DatabaseConnection


logger = logging.getLogger("SavdoLink.Pipeline")


class ETLPipeline:
    def __init__(
        self,
        config: Config,
        extractor: Optional[Any] = None,
        validator: Optional[Validator] = None,
        loader: Optional[StagingLoader] = None,
    ):
        self.config = config
        self.input_dir = Path(config.get("paths.incoming", "data/incoming"))
        self.archive_dir = Path(config.get("paths.archive", "data/archive"))

        # Extractor berilmagan bo'lsa, sukut bo'yicha CSV extractor yuklanadi
        if extractor is None:
            logger.info("Extractor ko'rsatilmadi. Sukut bo'yicha CSV extractor ishga tushirilmoqda.")
            self.extractor = get_extractor("csv")
        else:
            self.extractor = extractor

        self.validator = validator or Validator()
        self.loader = loader or StagingLoader(config.get("db", {}))

    def run(
        self,
        stage: str = "all",
        file_path: Optional[str] = None,
        dry_run: bool = False,
    ) -> Dict[str, int]:
        stats = {
            "rows_read": 0,
            "rows_valid": 0,
            "rows_rejected": 0,
            "rows_loaded": 0,
        }

        files_to_process = []
        if file_path:
            files_to_process.append(Path(file_path))
        elif self.input_dir.exists():
            files_to_process = list(self.input_dir.glob("*.csv"))

        if not files_to_process:
            logger.warning("Qayta ishlash uchun hech qanday CSV fayl topilmadi.")
            return stats

        for current_file in files_to_process:
            logger.info(f"Fayl qayta ishlanmoqda: {current_file.name}")

            # 1. Extract
            if stage in ["all", "extract"]:
                raw_data = self.extractor.extract(current_file)
                if not raw_data:
                    logger.warning(f"{current_file.name} ichidan ma'lumot o'qilmadi!")
                    continue
                stats["rows_read"] += len(raw_data)
            else:
                raw_data = []

            # 2. Transform & Validate
            valid_data = []
            if stage in ["all", "transform"] and raw_data:
                for row in raw_data:
                    validation_result = self.validator.validate(row)
                    if getattr(validation_result, "is_valid", False) or validation_result is True:
                        valid_data.append(row)
                        stats["rows_valid"] += 1
                    else:
                        stats["rows_rejected"] += 1
            elif stage != "extract":
                valid_data = raw_data

            # 3. Load
            if stage in ["all", "load"] and valid_data:
                loaded_count = self.loader.load(valid_data, dry_run=dry_run)
                stats["rows_loaded"] += loaded_count
                
                # Dry-run rejimida rollback chaqiruvini ta'minlash
                if dry_run:
                    if hasattr(self.loader, "rollback"):
                        self.loader.rollback()
                    elif hasattr(self.loader, "db") and hasattr(self.loader.db, "rollback"):
                        self.loader.db.rollback()
                    elif hasattr(self.loader, "connection") and hasattr(self.loader.connection, "rollback"):
                        self.loader.connection.rollback()

            # Archive processed file
            if not dry_run and stage == "all" and current_file.exists():
                self.archive_dir.mkdir(parents=True, exist_ok=True)
                target_path = self.archive_dir / current_file.name
                current_file.replace(target_path)
                logger.info(f"Fayl arxivga ko'chirildi: {target_path}")

        return stats  