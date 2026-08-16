import logging
import sys
from pathlib import Path


def get_logger(name: str, load_id: str) -> logging.Logger:
    """Fayl va konsolga belgilangan formatda log yozuvchi logger qaytaradi."""
    logger = logging.getLogger(name)

    # Takroriy handler'lar qo'shilishining oldini olish
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Log formati: 2026-08-10 14:22:31 | INFO | extract.csv | LOAD-20260810-142230 | 1042 qator o'qildi
    log_format = logging.Formatter(
        f"%(asctime)s | %(levelname)s | %(name)s | {load_id} | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Konsolga chiqarish (StreamHandler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # 2. Faylga yozish (FileHandler)
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    file_handler = logging.FileHandler(
        log_dir / f"{load_id}.log", encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger