import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class LoadLogger:
    """audit.LoadLog jadvali bilan ishlovchi sinf."""

    def __init__(self, cursor) -> None:
        self.cursor = cursor

    def is_already_loaded(self, source_file: str) -> bool:
        # P-09: oldin `return False` o'lik kod edi — idempotentlik ishlamay qolgan.
        """Fayl ilgari muvaffaqiyatli yuklangan bo'lsa True qaytaradi."""
        query = "SELECT 1 FROM audit.LoadLog WHERE SourceFile = ? AND Status = 'SUCCESS'"
        self.cursor.execute(query, (source_file,))
        return self.cursor.fetchone() is not None

    def start(self, load_id: str, source_file: str) -> int:
        """Yuklashni RUNNING holatida boshlab, LogID qaytaradi."""
        insert_query = """
            INSERT INTO audit.LoadLog (LoadId, SourceFile, Status, StartedAt)
            VALUES (?, ?, 'RUNNING', SYSDATETIME())
        """
        self.cursor.execute(insert_query, (load_id, source_file))

        # P-10: @@IDENTITY o'rniga SCOPE_IDENTITY — trigger boshqa IDENTITY bersa chalkashmasin.
        self.cursor.execute("SELECT CAST(SCOPE_IDENTITY() AS INT)")
        row = self.cursor.fetchone()
        log_id = int(row[0]) if row and row[0] is not None else 1

        logger.info(f"Load boshlandi [LogID: {log_id}, Fayl: {source_file}]")
        return log_id

    def finish(self, log_id: int, stats: Dict[str, int], status: str = "SUCCESS") -> None:
        """Jarayonni yakuniy ko'rsatkichlar bilan yopadi."""
        # P-10: WHERE LoadLogId = ? — aks holda barcha RUNNING qatorlar yangilanardi.
        query = """
            UPDATE audit.LoadLog
            SET Status = ?,
                RowsRead = ?,
                RowsValid = ?,
                RowsRejected = ?,
                RowsLoaded = ?,
                FinishedAt = SYSDATETIME()
            WHERE LoadLogId = ?;
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
        """Jarayonni FAILED holatiga o'tkazadi."""
        # S-07: ustun nomi ErrorMessage emas — audit.LoadLog da Message.
        # P-10: WHERE LoadLogId = ? majburiy.
        query = """
            UPDATE audit.LoadLog
            SET Status = 'FAILED',
                Message = ?,
                FinishedAt = SYSDATETIME()
            WHERE LoadLogId = ?;
        """
        self.cursor.execute(query, (message[:1000] if message else "Error", log_id))
        logger.error(f"Load muvaffaqiyatsiz [LogID: {log_id}]: {message}")
