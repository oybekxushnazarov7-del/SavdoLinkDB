from datetime import datetime
from pathlib import Path
import shutil
from typing import List, Tuple, Union

from src.exceptions import LoadError


def list_incoming(path: Path, pattern: str = "*") -> List[Path]:
    """
    Papka ichidagi berilgan andozaga (pattern) mos keladigan fayllarni
    alifbo/nomi bo'yicha saralab qaytaradi.
    """
    path = Path(path)
    if not path.exists() or not path.is_dir():
        return []

    # Faqat fayllarni oladi va nomiga ko'ra saralaydi
    files = [f for f in path.glob(pattern) if f.is_file()]
    return sorted(files)


def archive_file(src: Path, dst_dir: Path) -> Path:
    """
    Faylni belgilangan arxiv papkasiga ko'chiradi.
    Agar maqsad papkasi mavjud bo'lmasa, uni yaratadi.
    """
    src_path = Path(src)
    dst_directory = Path(dst_dir)

    dst_directory.mkdir(parents=True, exist_ok=True)
    dst_path = dst_directory / src_path.name

    # Faylni yangi manzilga ko'chirish
    return Path(shutil.move(str(src_path), str(dst_path)))


def full_sales_date_range(cursor) -> Tuple[str, str]:
    """core.SalesHeader dagi eng erta va eng kech savdo sanasini qaytaradi."""
    cursor.execute("""
        SELECT CAST(MIN(SaleDateTime) AS DATE), CAST(MAX(SaleDateTime) AS DATE)
        FROM core.SalesHeader
    """)
    row = cursor.fetchone()
    if not row or row[0] is None:
        raise LoadError(
            "core.SalesHeader bo'sh. Mumkin bo'lgan sabablar: "
            "(1) stg da bu LoadId uchun savdo qatori yo'q; "
            "(2) barcha qatorlar yetim havola tufayli tushib qolgan — "
            "audit.ErrorLog ni tekshiring; "
            "(3) usp_LoadSales chaqirilmagan."
        )
    return str(row[0]), str(row[1])


def make_load_id() -> str:
    """
    Vaqt tamg'asiga asoslangan noyob 'LOAD-YYYYMMDD-HHMMSS' kodi hosil qiladi.
    """
    now = datetime.now()
    return now.strftime("LOAD-%Y%m%d-%H%M%S")


def ensure_dirs(paths: dict) -> None:
    """
    Lug'atdagi barcha papka yo'llarini tekshiradi va yo'q bo'lsa yaratadi.
    """
    for key, path in paths.items():
        if path:
            dir_path = Path(path)
            dir_path.mkdir(parents=True, exist_ok=True)