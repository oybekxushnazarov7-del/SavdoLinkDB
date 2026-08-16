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
    """Ulanishni va tranzaksiyani boshqaradigan kontekst menejer.

    with DatabaseConnection(cfg) as cur:
        cur.execute(...)
    # xato bo'lmasa -> COMMIT, bo'lsa -> ROLLBACK, har holda close()
    """

    def __init__(self, cfg, logger=None):
        self.cfg = cfg
        self.logger = logger
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.conn = pyodbc.connect(build_connection_string(self.cfg))
        self.conn.autocommit = False          # MAJBURIY
        self.cursor = self.conn.cursor()
        self.cursor.fast_executemany = True
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self.conn.commit()
            else:
                self.conn.rollback()
                if self.logger:
                    self.logger.error("Tranzaksiya bekor qilindi: %s", exc_val)
        finally:
            self.cursor.close()
            self.conn.close()
        return False        # False -> xato yuqoriga uzatiladi 
