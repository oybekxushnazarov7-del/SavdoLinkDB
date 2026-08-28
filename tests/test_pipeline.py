"""
R-09: pipeline dry-run haqiqiy DatabaseConnection API si bilan.
"""
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.config import Config
from src.pipeline import ETLPipeline
from src.validate.validator import Validator
from src.validate.rules import DEFAULT_RULES


@patch("src.pipeline.DatabaseConnection")
def test_pipeline_dry_run_rollback(mock_db_cls, tmp_path):
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor = mock_cursor
    # Idempotentlik: hali yuklanmagan; keyin OUTPUT INSERTED.LoadLogId
    mock_cursor.fetchone.side_effect = [None, (1,)]
    mock_db_cls.return_value.__enter__.return_value = mock_conn

    # Bo'sh incoming — fayl yo'q, lekin dry-run rollback chaqirilishi kerak emas
    # (fayl bo'lmasa erta return). Bitta minimal CSV yasaymiz.
    sales = tmp_path / "sales_2026-01-14.csv"
    sales.write_text(
        "receipt_no;store_code;cashier_id;sale_datetime;sku;qty;unit_price;discount_pct;payment_type\n"
        "R-0000001;ST-001;E-0101;2026-01-14 10:00:00;SKU-00001;2;10000,00;0;CASH\n",
        encoding="utf-8",
    )

    config = Config({
        "db": {"driver": "ODBC Driver 17 for SQL Server", "server": "localhost",
               "database": "SavdoLinkDB", "trusted_connection": True},
        "paths": {
            "incoming": str(tmp_path),
            "archive": str(tmp_path / "archive"),
            "rejected": str(tmp_path / "rejected"),
        },
        "load": {"batch_size": 100},
    })

    pipeline = ETLPipeline(config, validator=Validator(DEFAULT_RULES))
    stats = pipeline.run(stage="all", dry_run=True)

    mock_conn.rollback.assert_called()
    assert "rows_read" in stats
