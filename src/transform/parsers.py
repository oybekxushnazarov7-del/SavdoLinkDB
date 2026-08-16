from datetime import datetime,date
from decimal import Decimal, InvalidOperation

DATETIME_FORMATS = (
    "%Y-%m-%d %H:%M:%S",
    "%d.%m.%Y %H:%M",
    # ... profiling'da topgan boshqa formatlaringizni qo'shing
)

DATE_FORMATS = (
    "%Y-%m-%d",
    "%d.%m.%Y",
    "%d/%m/%Y",
    "%d-%m-%Y",
)

def parse_datetime(value):
    """Matnni datetime ga aylantiradi.

    Formatlar ro'yxatini birma-bir sinab ko'radi. Hech biri mos kelmasa None.
    Xato chaqirmaydi - qaror qabul qilish validatorning ishi.
    """
    if value is None:
        return None
    text = value.strip()
    if not text:
        return None
    for fmt in DATETIME_FORMATS:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None

def parse_date(value):
    if value is None:
        return None 
    text = value.strip()
    if not text:
        return  None

    dt = parse_datetime(text)
    if dt:
        return dt.date()

    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None 

def parse_decimal(value):
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None

    text = text.replace(" ", "")

    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    else:
        text = text.replace(",", ".")

    try:
        return Decimal(text)
    except (InvalidOperation, TypeError):
        return None

def parse_int(value):
    if value is None:
        return None

    text = str(value).strip() 
    if not text:
        return None

    try:
        return int(text)
    except ValueError:
        dec = parse_decimal(text)
        if dec is not None and dec % 1 == 0:
            return int(dec)
        return None

def parse_bool(value):
    if value is None:
        return None

    if isinstance(value, bool):
        return value

    text = str(value).strip().lower()
    if not text:
        return None

    true_values = {"true", "ha", "yes", "1", "y", "t", "dha"}
    false_values = {"false", "yo'q", "yoq", "no", "0", "n", "f"}

    if text in true_values:
        return True
    if text in false_values:
        return False

def detect_date_format(value):
    if value is None:
        return None

    text = str(value).strip()
    if not text:
        return None

    all_formats = DATETIME_FORMATS + DATE_FORMATS
    for fmt in all_formats:
        try:
            datetime.strptime(text, fmt)
            return fmt
        except ValueError:
            continue

    return None