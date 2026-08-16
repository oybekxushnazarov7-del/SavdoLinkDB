from typing import Any, Callable, Dict, List, Optional


def completeness(records: List[Dict[str, Any]], fields: List[str]) -> float:
    """To'ldirilgan maydonlar ulushini (foizda: 0.0 - 100.0) hisoblaydi."""
    if not records or not fields:
        return 100.0

    total_cells = len(records) * len(fields)
    filled_cells = 0

    for record in records:
        for field in fields:
            val = record.get(field)
            # None yoki bo'sh satr bo'lmasa, to'ldirilgan deb hisoblanadi
            if val is not None and str(val).strip() != "":
                filled_cells += 1

    return round((filled_cells / total_cells) * 100, 2)


def uniqueness(
    records: List[Dict[str, Any]], key_func: Callable[[Dict[str, Any]], Any]
) -> float:
    """Unikallik ulushini hisoblaydi: 100 * (1 - dublikatlar / jami)."""
    if not records:
        return 100.0

    seen_keys = set()
    duplicates_count = 0

    for record in records:
        key = key_func(record)
        if key in seen_keys:
            duplicates_count += 1
        else:
            seen_keys.add(key)

    uniqueness_pct = (1.0 - (duplicates_count / len(records))) * 100
    return round(max(0.0, uniqueness_pct), 2)


def validity(total: int, rejected: int) -> float:
    """Validatsiya qoidalaridan muvaffaqiyatli o'tgan yozuvlar ulushini hisoblaydi."""
    if total <= 0:
        return 100.0

    valid_count = total - rejected
    validity_pct = (valid_count / total) * 100
    return round(max(0.0, validity_pct), 2)


def consistency(records: List[Dict[str, Any]], catalog: Any) -> float:
    """Havolalari to'g'ri chiqqan (katalogda mavjud bo'lgan) yozuvlar ulushini hisoblaydi."""
    if not records:
        return 100.0

    valid_refs = 0
    total_refs = 0

    for record in records:
        sku = record.get("sku")
        if sku is not None:
            total_refs += 1
            if sku in catalog:
                valid_refs += 1

    if total_refs == 0:
        return 100.0

    return round((valid_refs / total_refs) * 100, 2)


def build_report(
    records: List[Dict[str, Any]],
    rejected_count: int,
    required_fields: List[str],
    key_func: Callable[[Dict[str, Any]], Any],
    catalog: Any,
    thresholds: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Barcha DQ (Data Quality) ko'rsatkichlarini jamlab, umumiy hisobot lug'atini shakllantiradi."""
    total_records = len(records)
    
    comp_score = completeness(records, required_fields)
    uniq_score = uniqueness(records, key_func)
    val_score = validity(total_records, rejected_count)
    cons_score = consistency(records, catalog)

    # Standart chegaralar (thresholds)
    default_thresholds = {
        "min_completeness_pct": 95.0,
        "min_uniqueness_pct": 98.0,
        "min_validity_pct": 85.0,
        "min_consistency_pct": 90.0,
    }
    if thresholds:
        default_thresholds.update(thresholds)

    # Chegaralarga muvofiqlik tekshiruvi (PASS/FAIL)
    status = (
        comp_score >= default_thresholds["min_completeness_pct"]
        and uniq_score >= default_thresholds["min_uniqueness_pct"]
        and val_score >= default_thresholds["min_validity_pct"]
        and cons_score >= default_thresholds["min_consistency_pct"]
    )

    return {
        "summary": {
            "total_records": total_records,
            "rejected_records": rejected_count,
            "passed_records": total_records - rejected_count,
            "overall_status": "PASS" if status else "FAIL",
        },
        "metrics": {
            "completeness_pct": comp_score,
            "uniqueness_pct": uniq_score,
            "validity_pct": val_score,
            "consistency_pct": cons_score,
        },
        "thresholds": default_thresholds,
    }

