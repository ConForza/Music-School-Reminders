import sqlite3

class Connection:

    def __init__(self, db_path: str = "audits.db"):
        self.db_path = db_path

    def create_connection(self):
        return sqlite3.connect(self.db_path)

    def create_table(self):
        conn = self.create_connection()
        conn.execute("""CREATE TABLE IF NOT EXISTS audit_logs
                     (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         timestamp TEXT NOT NULL,
                         command TEXT NOT NULL,
                         source_id TEXT NOT NULL,
                         args TEXT NOT NULL,
                         result_type TEXT NOT NULL,
                         routing TEXT,
                         errors TEXT,
                         status TEXT NOT NULL
                     )
            """)
        conn.commit()
        conn.close()