"""
R-09: haqiqiy LoadLogger kodini sinaydi (mock list bilan «test teatri» emas).
"""
from unittest.mock import MagicMock

from src.load.load_log import LoadLogger


def test_is_already_loaded_topadi():
    cur = MagicMock()
    cur.fetchone.return_value = (1,)  # baza qator qaytardi
    log = LoadLogger(cur)
    assert log.is_already_loaded("sales_2026-01-14.csv") is True
    cur.execute.assert_called_once()


def test_is_already_loaded_topmadi():
    cur = MagicMock()
    cur.fetchone.return_value = None
    log = LoadLogger(cur)
    assert log.is_already_loaded("yangi.csv") is False


def test_finish_where_loadlogid():
    # P-10: UPDATE WHERE LoadLogId = ?
    cur = MagicMock()
    log = LoadLogger(cur)
    log.finish(42, {"rows_read": 10, "rows_valid": 8, "rows_rejected": 2, "rows_loaded": 8})
    args = cur.execute.call_args[0]
    sql = args[0]
    params = args[1]
    assert "LoadLogId" in sql
    assert params[-1] == 42


def test_fail_uses_message_column():
    # S-07: ErrorMessage emas Message
    cur = MagicMock()
    log = LoadLogger(cur)
    log.fail(7, "boom")
    sql = cur.execute.call_args[0][0]
    assert "Message" in sql
    assert "ErrorMessage" not in sql
