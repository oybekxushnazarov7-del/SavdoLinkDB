"""B-04: Validator.from_config JSON dan qoidalarni o'qishi."""
import json

from src.validate.validator import Validator


def test_from_config_reads_json(tmp_path):
    cfg = {
        "rules": {
            "SKU_REQUIRED": {"enabled": True, "severity": "ERROR"},
            "QTY_POSITIVE": {"enabled": False, "severity": "ERROR"},
            "DISCOUNT_RANGE": {
                "enabled": True,
                "severity": "ERROR",
                "min": 0,
                "max": 50,
            },
        },
        "thresholds": {"max_reject_pct": 10.0},
    }
    path = tmp_path / "rules.json"
    path.write_text(json.dumps(cfg), encoding="utf-8")

    validator = Validator.from_config(str(path))
    codes = {r.code for r in validator.rules}
    assert "SKU_REQUIRED" in codes
    assert "QTY_POSITIVE" not in codes

    disc = next(r for r in validator.rules if r.code == "DISCOUNT_RANGE")
    assert disc.max_pct == 50
