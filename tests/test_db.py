from unittest.mock import MagicMock, patch
import pytest
from src.load.db import DatabaseConnection, build_connection_string


def test_build_connection_string_trusted():
    """Trusted Connection (Windows Authentication) uchun ulanish satrini tekshirish."""
    cfg = {
        "driver": "ODBC Driver 17 for SQL Server",
        "server": "localhost",
        "database": "SavdoLinkDB",
        "trusted_connection": True,
    }
    conn_str = build_connection_string(cfg)
    assert "DRIVER={ODBC Driver 17 for SQL Server}" in conn_str
    assert "SERVER=localhost" in conn_str
    assert "DATABASE=SavdoLinkDB" in conn_str
    assert "Trusted_Connection=yes" in conn_str


def test_build_connection_string_sql_auth():
    """SQL Server Authentication (Login va Parol) uchun ulanish satrini tekshirish."""
    cfg = {
        "driver": "ODBC Driver 17 for SQL Server",
        "server": "localhost",
        "database": "SavdoLinkDB",
        "trusted_connection": False,
        "user": "sa",
        "password": "SecretPassword123",
    }
    conn_str = build_connection_string(cfg)
    assert "UID=sa" in conn_str
    assert "PWD=SecretPassword123" in conn_str


@patch("pyodbc.connect")
def test_database_connection_commit_on_success(mock_connect):
    """Muvaffaqiyatli tranzaksiya yakunlanganda commit() chaqirilishini tekshirish."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    cfg = {
        "driver": "ODBC Driver 17 for SQL Server",
        "server": "localhost",
        "database": "SavdoLinkDB",
        "trusted_connection": True,
    }

    with DatabaseConnection(cfg) as cursor:
        cursor.execute("SELECT 1")

    # Commit va Close chaqirilganini tekshiramiz
    mock_conn.commit.assert_called_once()
    mock_conn.rollback.assert_not_called()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()


@patch("pyodbc.connect")
def test_database_connection_rollback_on_error(mock_connect):
    """Xatolik yuz berganda rollback() chaqirilishini va xato berkitilmasligini tekshirish."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_connect.return_value = mock_conn

    cfg = {
        "driver": "ODBC Driver 17 for SQL Server",
        "server": "localhost",
        "database": "SavdoLinkDB",
        "trusted_connection": True,
    }

    # Xatolik tashlanganda rollback chaqirilishini tekshiramiz
    with pytest.raises(ValueError, match="Sinov xatoligi"):
        with DatabaseConnection(cfg) as cursor:
            raise ValueError("Sinov xatoligi")

    mock_conn.rollback.assert_called_once()
    mock_conn.commit.assert_not_called()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()