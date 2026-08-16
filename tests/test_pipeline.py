from unittest.mock import MagicMock, patch
from src.pipeline import ETLPipeline


@patch("src.pipeline.DatabaseConnection")
def test_pipeline_dry_run(mock_db):
    mock_cursor = MagicMock()
    mock_db.return_value.__enter__.return_value = mock_cursor

    config = {
        "db": {"driver": "SQL Server", "server": "localhost", "database": "test_db"},
        "input_dir": "data/raw",
    }

    pipeline = ETLPipeline(config)
    # Dry run bilan ishga tushirish
    pipeline.run(stage="all", dry_run=True)

    # Dry-run rejimida rollback chaqirilishi kerak
    mock_cursor.connection.rollback.assert_called()