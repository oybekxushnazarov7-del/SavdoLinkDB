from decimal import Decimal 
from datetime import date, datetime

def money(value, currency = "so'm") -> str:
    if value is None:
        return "-"
    try:
        val = Decimal(str(value))
        formatted = f"{val:,.2f}".replace(",", " ").replace(".", ",")
        return f"{formatted} {currency}"
    except Exception:
        return f"0,00 {currency}"

def percent(value) -> str:
    if value is None:
        return "0,0 %"
    try:
        value = float(value)
        return f"{value:,.1f} %".replace(".", ",")
    except Exception:
        return "0,0 %"

def uzdate(value) -> str:
    if not value:
        return "-"
    if isinstance(value, (date, datetime)):
        return value.strftime("%d.%m.%Y")
    return str(value)

def thousands(value) -> str:
    if value is None:
        return "0"
    try:
        return f"{int(value):,}".replace(",", " ")
    except Exception:
        return "0"

def delta_class(value) -> str:
    try:
        val = float(value or 0)
        return "up" if val >= 0 else "down"
    except Exception:
        return "up"

def register_filters(env):
    env.filters("money") = money 
    env.filters["percent"] = percent
    env.filters["uzdate"] = uzdate
    env.filters["thousands"] = thousands
    env.filters["delta_class"] = delta_class