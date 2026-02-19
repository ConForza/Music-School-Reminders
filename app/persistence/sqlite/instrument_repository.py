import sqlite3

from app.persistence.sqlite.connection import Connection


class InstrumentRepository:

    def __init__(self):
        self.connection = Connection()

    def get_in_person_appointment_type_ids(self, instrument: str) -> dict:
        conn = self.connection.create_connection()
        c = conn.cursor()

        def fetch(duration :int):
            c.execute(
                """
                SELECT appointment_code
                FROM instruments
                WHERE instrument = ? COLLATE NOCASE
                    AND duration = ?
                    AND is_video_lesson = 0
                """,
                (instrument, duration)
            )
            row = c.fetchone()
            return int(row[0]) if row is not None and row[0] is not None else None

        return {"30": fetch(30), "60": fetch(60)}
