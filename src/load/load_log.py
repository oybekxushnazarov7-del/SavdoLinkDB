import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class LoadLogger:
    """audit.LoadLog jadvali bilan ishlovchi sinf[cite: 1]."""

    def __init__(self, cursor) -> None:
        self.cursor = cursor

    def is_already_loaded(self, source_file: str) -> bool:
        """Fayl ilgari muvaffaqiyatli yuklangan bo'lsa True qaytaradi[cite: 1]."""
        query = "SELECT 1 FROM audit.LoadLog WHERE SourceFile = ? AND Status = 'SUCCESS'"
        self.cursor.execute(query, (source_file,))
        return self.cursor.fetchone() is not None

    def start(self, load_id: str, source_file: str) -> int:
        """Yuklashni RUNNING holatida boshlab, LogID qaytaradi[cite: 1]."""
        query = """
            INSERT INTO audit.LoadLog (LoadId, SourceFile, Status, StartedAt)
            OUTPUT INSERTED.LogId
            VALUES (?, ?, 'RUNNING', GETDATE())
        """
        self.cursor.execute(query, (load_id, source_file))
        log_id = self.cursor.fetchone()[0]
        logger.info(f"Load boshlandi [LogID: {log_id}, Fayl: {source_file}]")
        return log_id

    def finish(self, log_id: int, stats: Dict[str, int], status: str = "SUCCESS") -> None:
        """Jarayonni yakuniy ko'rsatkichlar bilan yopadi[cite: 1]."""
        query = """
            UPDATE audit.LoadLog
            SET Status = ?,
                RowsRead = ?,
                RowsValid = ?,
                RowsRejected = ?,
                RowsLoaded = ?,
                FinishedAt = GETDATE()
            WHERE LogId = ?
        """
        self.cursor.execute(
            query,
            (
                status,
                stats.get("rows_read", 0),
                stats.get("rows_valid", 0),
                stats.get("rows_rejected", 0),
                stats.get("rows_loaded", 0),
                log_id,
            ),
        )
        logger.info(f"Load yakunlandi [LogID: {log_id}, Status: {status}]")

    def fail(self, log_id: int, message: str) -> None:
        """Jarayonni FAILED holatiga o'tkazadi[cite: 1]."""
        query = """
            UPDATE audit.LoadLog
            SET Status = 'FAILED',
                ErrorMessage = ?,
                FinishedAt = GETDATE()
            WHERE LogId = ?
        """
        self.cursor.execute(query, (message[:1000] if message else "Error", log_id))
        logger.error(f"Load muvaffaqiyatsiz [LogID: {log_id}]: {message}")