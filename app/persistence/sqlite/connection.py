import sqlite3

class Connection:

    def __init__(self, db_path: str = "main.db"):
        self.db_path = db_path

    def create_connection(self):
        return sqlite3.connect(self.db_path)

    def create_tables(self):
        conn = self.create_connection()
        c = conn.cursor()

        c.execute("""
                  CREATE TABLE IF NOT EXISTS users
                  (
                      id            INTEGER PRIMARY KEY AUTOINCREMENT,
                      email         TEXT UNIQUE,
                      password_hash TEXT,
                      discord_id    TEXT UNIQUE,
                      is_admin      INTEGER NOT NULL DEFAULT 0,
                      created_at    TEXT    NOT NULL
                  )
                  """)

        c.execute("""
                  CREATE TABLE IF NOT EXISTS staff
                  (
                      id                 INTEGER PRIMARY KEY AUTOINCREMENT,
                      user_id            INTEGER NOT NULL,
                      first_name         TEXT,
                      surname            TEXT,
                      role               TEXT,
                      acuity_calendar_id INTEGER,
                      FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                  )
                  """)

        c.execute("""
                  CREATE TABLE IF NOT EXISTS students
                  (
                      id         INTEGER PRIMARY KEY AUTOINCREMENT,
                      first_name TEXT,
                      surname    TEXT,
                      email      TEXT
                  )
                  """)

        c.execute("""
                  CREATE TABLE IF NOT EXISTS staff_students
                  (
                      staff_id   INTEGER NOT NULL,
                      student_id INTEGER NOT NULL,
                      PRIMARY KEY (staff_id, student_id),
                      FOREIGN KEY (staff_id) REFERENCES staff (id) ON DELETE CASCADE,
                      FOREIGN KEY (student_id) REFERENCES students (id) ON DELETE CASCADE
                  )
                  """)

        c.execute("""CREATE TABLE IF NOT EXISTS audit_logs
                     (
                         id INTEGER PRIMARY KEY AUTOINCREMENT,
                         user_id INTEGER,
                         timestamp TEXT NOT NULL,
                         command TEXT NOT NULL,
                         source_id TEXT NOT NULL,
                         args TEXT NOT NULL,
                         result_type TEXT NOT NULL,
                         routing TEXT,
                         errors TEXT,
                         status TEXT NOT NULL,
                         FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
                     )
            """)
        conn.commit()
        conn.close()