import pyodbc


def build_connection_string(cfg):
    """Sozlama lug'atidan ODBC ulanish satrini yasaydi."""
    parts = [
        f"DRIVER={{{cfg['driver']}}}",
        f"SERVER={cfg['server']}",
        f"DATABASE={cfg['database']}",
    ]
    if cfg.get("trusted_connection"):
        parts.append("Trusted_Connection=yes")
    else:
        parts.append(f"UID={cfg['user']};PWD={cfg['password']}")
    return ";".join(parts)


class DatabaseConnection:
    """Ulanish va cursorni birgalikda boshqaruvchi kontekst menejer."""

    def __init__(self, cfg, logger=None):
        self.cfg = cfg
        self.logger = logger
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = pyodbc.connect(build_connection_string(self.cfg))
        self.conn.autocommit = False  # Tranzaksiyani qo'lda commit qilish
        self.cursor = self.conn.cursor()
        self.cursor.fast_executemany = True
        return self

    def execute(self, query, params=None):
        if params:
            return self.cursor.execute(query, params)
        return self.cursor.execute(query)

    def executemany(self, query, params):
        return self.cursor.executemany(query, params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        if self.conn:
            self.conn.commit()

    def rollback(self):
        if self.conn:
            self.conn.rollback()

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                if self.logger:
                    self.logger.error("Tranzaksiya bekor qilindi: %s", exc_val)
        except Exception as commit_err:
            if self.logger:
                self.logger.error("Commit/Rollback xatosi: %s", commit_err)
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
        return False