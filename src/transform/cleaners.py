import re
from typing import Any, Callable, Dict, Optional, Union

# Unicode dagi barcha ko'rinmas bo'shliq belgilari uchun regas (non-breaking space va b.)
UNICODE_SPACES_RE = re.compile(r"[\s\u200b\u200c\u200d\ufeff\xa0]+")


def collapse_spaces(value: Optional[str]) -> str:
    """Ichkaridagi ketma-ket bo'shliqlarni va ko'rinmas Unicode belgilarni bittaga keltirib tozalaydi."""
    if value is None:
        return ""

    text = str(value)
    # Barcha turdagi bo'shliqlarni bitta standart ' ' ga almashtirish va chetlarini tozalash
    cleaned = UNICODE_SPACES_RE.sub(" ", text).strip()
    return cleaned


def normalize_text(value: Optional[str]) -> str:
    """Ortiqcha bo'shliqlarni olib tashlaydi (chetdagi va ichki takrorlanuvchi)."""
    return collapse_spaces(value)


def normalize_code(value: Optional[str]) -> str:
    """Kodlar va identifikatorlar uchun: barcha bo'shliqlarni olib tashlaydi va katta harfga o'tkazadi."""
    if value is None:
        return ""

    text = str(value)
    # Barcha bo'shliqlarni butunlay olib tashlash
    no_spaces = UNICODE_SPACES_RE.sub("", text)
    return no_spaces.upper()


def empty_to_none(value: Optional[str]) -> Optional[str]:
    """Bo'sh satr, bo'shliqlardan iborat satr va 'n/a', 'null', 'none' kabi qiymatlarni None ga o'tkazadi."""
    if value is None:
        return None

    cleaned = collapse_spaces(str(value))
    if not cleaned:
        return None

    # Profiling jarayonida ko'p uchraydigan "bo'sh" matn qiymatlari
    null_representers = {"n/a", "na", "null", "none", "nan", "-", "--", "undefined"}
    if cleaned.lower() in null_representers:
        return None

    return cleaned


def clean_row(
    row: Dict[str, Any],
    spec: Dict[str, Union[Callable[[Any], Any], list[Callable[[Any], Any]]]]
) -> Dict[str, Any]:
    """
    Butun qatorga spec lug'atida ko'rsatilgan qoidalarni qo'llaydi.
    
    `spec` strukturasi:
    {
        "sku": normalize_code,
        "receipt_no": [normalize_text, empty_to_none]  # Zanjir bo'lib ishlashi ham mumkin
    }
    """
    cleaned_row = row.copy()

    for column, func_or_funcs in spec.items():
        if column in cleaned_row:
            val = cleaned_row[column]

            if callable(func_or_funcs):
                cleaned_row[column] = func_or_funcs(val)
            elif isinstance(func_or_funcs, (list, tuple)):
                # Agar bir nechta funksiyalar ketma-ket berilgan bo'lsa (pipeline)
                for func in func_or_funcs:
                    val = func(val)
                cleaned_row[column] = val

    return cleaned_row 