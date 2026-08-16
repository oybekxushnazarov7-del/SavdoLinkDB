from collections import Counter
import json
from typing import Dict, Iterable, List, Tuple

from src.validate.rules import ValidationRule
import src.validate.rules as rule_modules


# ==============================================================================
# VALIDATION RESULT SINF
# ==============================================================================

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
        """'if result:' ko'rinishida ishlashi uchun is_valid qiymatini qaytaradi."""
        return self.is_valid

    def __len__(self) -> int:
        """Jami buzilgan (ERROR + WARNING) qoidalar sonini qaytaradi."""
        return len(self.errors) + len(self.warnings)

    def __repr__(self) -> str:
        return (
            f"<ValidationResult valid={self.is_valid} "
            f"errors={len(self.errors)} warnings={len(self.warnings)}>"
        )


# ==============================================================================
# VALIDATOR SINF
# ==============================================================================

class Validator:
    """Ma'lumotlar oqimini qoidalar to'plami bo'yicha tekshiruvchi va statistika yig'uvchi sinf."""

    def __init__(self, rules: List[ValidationRule]) -> None:
        self.rules = rules
        self._stats = Counter()

    def validate(self, record: dict) -> ValidationResult:
        """Bitta yozuvni barcha qoidalar bo'yicha tekshiradi."""
        errors: List[ValidationRule] = []
        warnings: List[ValidationRule] = []

        for rule in self.rules:
            # Agar qoida buzilsa (check False qaytarsa)
            if not rule.check(record):
                self._stats[rule.code] += 1
                if rule.severity == "ERROR":
                    errors.append(rule)
                else:
                    warnings.append(rule)

        return ValidationResult(record=record, errors=errors, warnings=warnings)

    def validate_batch(self, records: Iterable[dict]) -> Tuple[List[dict], List[dict]]:
        """Ko'p sonli yozuvlarni birdaniga tekshirib, ikkita ro'yxatga ajratadi.
        
        Qaytaradi: (yaroqli_yozuvlar, rad_etilgan_yozuvlar)
        """
        valid_records = []
        rejected_records = []

        for record in records:
            result = self.validate(record)
            if result.is_valid:
                valid_records.append(record)
            else:
                # Rad etilgan yozuvga buzilgan qoidalar haqida ma'lumot qistirib ketish
                rejected_item = record.copy()
                rejected_item["_errors"] = [e.code for e in result.errors]
                rejected_records.append(rejected_item)

        return valid_records, rejected_records

    @property
    def stats(self) -> Dict[str, int]:
        """Har bir qoida necha marta buzilganligining statistikasini qaytaradi."""
        return dict(self._stats)

    @classmethod
    def from_config(cls, path: str) -> "Validator":
        """JSON konfiguratsiya faylidan qoidalarni o'qib, Validator obyektini quradi."""
        with open(path, "r", encoding="utf-8") as f:
            config = json.load(f)

        rules_list = []
        # JSON fayldagi qoida nomlarini tegishli sinfga dinamik ravishda bog'lash
        for rule_cfg in config.get("rules", []):
            rule_class_name = rule_cfg.get("class_name")
            if hasattr(rule_modules, rule_class_name):
                rule_cls = getattr(rule_modules, rule_class_name)
                rules_list.append(rule_cls())

        return cls(rules=rules_list)