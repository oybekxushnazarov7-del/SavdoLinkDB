from collections import Counter
import json
from typing import Dict, Iterable, List, Tuple

from src.exceptions import ConfigError
from src.validate.rules import (
    ValidationRule,
    SkuRequiredRule,
    SaleDateRequiredRule,
    QtyIsIntRule,
    QtyPositiveRule,
    PriceIsNumericRule,
    DiscountRangeRule,
    PriceDeviationRule,
    CashierStoreRule,
    SkuExistsRule,
    StoreExistsRule,
    FutureDateRule,
    ReturnAfterSaleRule,
)


# P-14: JSON da class_name yo'q — qoida KODI bo'yicha xarita
RULE_REGISTRY = {
    "SKU_REQUIRED": SkuRequiredRule,
    "DATE_REQUIRED": SaleDateRequiredRule,
    "QTY_IS_INT": QtyIsIntRule,
    "QTY_POSITIVE": QtyPositiveRule,
    "PRICE_IS_NUMERIC": PriceIsNumericRule,
    "DISCOUNT_RANGE": DiscountRangeRule,
    "PRICE_DEVIATION": PriceDeviationRule,
    "CASHIER_STORE": CashierStoreRule,
    "SKU_EXISTS": SkuExistsRule,
    "STORE_EXISTS": StoreExistsRule,
    "FUTURE_DATE": FutureDateRule,
    "RETURN_AFTER_SALE": ReturnAfterSaleRule,
}


class ValidationResult:
    """Tekshiruv natijasini saqlovchi va qayta ishlovchi obyekt."""

    def __init__(
        self,
        record: dict,
        errors: List[ValidationRule] = None,
        warnings: List[ValidationRule] = None,
    ) -> None:
        self.record = record
        self.errors = errors if errors is not None else []
        self.warnings = warnings if warnings is not None else []

    @property
    def is_valid(self) -> bool:
        """Hech qanday ERROR turidagi qoida buzilmagan bo'lsa True qaytaradi."""
        return len(self.errors) == 0

    def __bool__(self) -> bool:
        return self.is_valid

    def __len__(self) -> int:
        return len(self.errors) + len(self.warnings)

    def __repr__(self) -> str:
        return (
            f"<ValidationResult valid={self.is_valid} "
            f"errors={len(self.errors)} warnings={len(self.warnings)}>"
        )


class Validator:
    """Ma'lumotlar oqimini qoidalar to'plami bo'yicha tekshiruvchi sinf."""

    def __init__(self, rules: List[ValidationRule]) -> None:
        # P-04: rules majburiy — argumentsiz Validator() TypeError
        self.rules = rules
        self._stats = Counter()

    def validate(self, record: dict) -> ValidationResult:
        errors: List[ValidationRule] = []
        warnings: List[ValidationRule] = []

        for rule in self.rules:
            if not rule.check(record):
                self._stats[rule.code] += 1
                if rule.severity == "ERROR":
                    errors.append(rule)
                else:
                    warnings.append(rule)

        return ValidationResult(record=record, errors=errors, warnings=warnings)

    def validate_batch(self, records: Iterable[dict]) -> Tuple[List[dict], List[dict]]:
        valid_records = []
        rejected_records = []

        for record in records:
            result = self.validate(record)
            if result.is_valid:
                valid_records.append(record)
            else:
                rejected_item = record.copy()
                rejected_item["_errors"] = [e.code for e in result.errors]
                rejected_records.append(rejected_item)

        return valid_records, rejected_records

    @property
    def stats(self) -> Dict[str, int]:
        return dict(self._stats)

    @classmethod
    def from_config(cls, path: str) -> "Validator":
        # P-14: rules — lug'at {CODE: {enabled, severity, ...}}, ro'yxat emas
        with open(path, "r", encoding="utf-8") as f:
            cfg = json.load(f)

        rules = []
        for code, params in cfg.get("rules", {}).items():
            if not params.get("enabled", True):
                continue
            rule_cls = RULE_REGISTRY.get(code)
            if rule_cls is None:
                raise ConfigError(f"Noma'lum qoida kodi: {code}")

            # P-15: PriceDeviationRule max_factor konfiguratsiyadan
            if code == "PRICE_DEVIATION":
                rule = rule_cls(max_factor=float(params.get("max_factor", 1.5)))
            elif code == "DISCOUNT_RANGE":
                rule = rule_cls(
                    min_pct=float(params.get("min", 0)),
                    max_pct=float(params.get("max", 100)),
                )
            else:
                rule = rule_cls()

            rule.severity = params.get("severity", rule.severity)
            rules.append(rule)

        return cls(rules)
