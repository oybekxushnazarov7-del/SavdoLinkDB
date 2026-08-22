import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class LoadLogger:
    """audit.LoadLog jadvali bilan ishlovchi sinf."""

    def __init__(self, cursor) -> None:
        self.cursor = cursor

    def is_already_loaded(self, source_file: str) -> bool:
        """Fayl ilgari muvaffaqiyatli yuklangan bo'lsa True qaytaradi."""
        query = "SELECT 1 FROM audit.LoadLog WHERE SourceFile = ? AND Status = 'SUCCESS'"
        self.cursor.execute(query, (source_file,))
        return self.cursor.fetchone() is not None

    def start(self, load_id: str, source_file: str) -> int:
        """Yuklashni RUNNING holatida boshlab, LogID qaytaradi."""
        insert_query = """
            INSERT INTO audit.LoadLog (LoadId, SourceFile, Status, StartedAt)
            VALUES (?, ?, 'RUNNING', GETDATE())
        """
        self.cursor.execute(insert_query, (load_id, source_file))

        select_query = "SELECT @@IDENTITY"
        self.cursor.execute(select_query)
        row = self.cursor.fetchone()
        log_id = int(row[0]) if row and row[0] is not None else 1

        logger.info(f"Load boshlandi [LogID: {log_id}, Fayl: {source_file}]")
        return log_id

    def finish(self, log_id: int, stats: Dict[str, int], status: str = "SUCCESS") -> None:
        """Jarayonni yakuniy ko'rsatkichlar bilan yopadi."""
        query = """
            UPDATE audit.LoadLog
            SET Status = ?,
                RowsRead = ?,
                RowsValid = ?,
                RowsRejected = ?,
                RowsLoaded = ?,
                FinishedAt = GETDATE()
            WHERE Status = 'RUNNING' AND SourceFile IS NOT NULL;
        """
        self.cursor.execute(
            query,
            (
                status,
                stats.get("rows_read", 0),
                stats.get("rows_valid", 0),
                stats.get("rows_rejected", 0),
                stats.get("rows_loaded", 0),
            ),
        )
        logger.info(f"Load yakunlandi [LogID: {log_id}, Status: {status}]")

    def fail(self, log_id: int, message: str) -> None:
        """Jarayonni FAILED holatiga o'tkazadi."""
        query = """
            UPDATE audit.LoadLog
            SET Status = 'FAILED',
                ErrorMessage = ?,
                FinishedAt = GETDATE()
            WHERE Status = 'RUNNING';
        """
        self.cursor.execute(query, (message[:1000] if message else "Error",))
        logger.error(f"Load muvaffaqiyatsiz [LogID: {log_id}]: {message}")