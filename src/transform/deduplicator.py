def deduplicate(records, key_func):
    """Dublikatlarni ajratadi. Birinchi uchragan yozuv qoladi.

    key_func - yozuvdan noyoblik kalitini oladigan funksiya.
    Qaytaradi: (noyob_yozuvlar, dublikatlar)
    """
    seen = set()
    unique, duplicates = [], []
    for record in records:
        key = key_func(record)
        if key in seen:
            duplicates.append(record)
        else:
            seen.add(key)
            unique.append(record)
    return unique, duplicates
