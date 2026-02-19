import sqlite3

from app.persistence.sqlite.connection import Connection


class InstrumentRepository:

    def __init__(self):
        self.connection = Connection()

    def instrument_exists(self, instrument: str) -> bool:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute(
            """
            SELECT 1
            FROM instruments
            WHERE instrument = ? COLLATE NOCASE
            LIMIT 1
            """,
            (instrument,)
        )
        row = c.fetchone()
        conn.close()
        return row is not None

    def get_certificate_code(self, instrument, duration):
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute(
            """
            SELECT certificate_code
            FROM instruments
            WHERE instrument = ? COLLATE NOCASE
                AND duration = ?
                AND is_video_lesson = 0
            """,
            (instrument, duration)
        )
        row = c.fetchone()
        conn.close()
        return row[0] if row is not None and row[0] is not None else None

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

        ids_30 = fetch(30)
        ids_60 = fetch(60)

        conn.close()
        return {"30": ids_30, "60": ids_60}

    def search_instruments(self, prefix: str, limit: int = 25) -> list[str]:
        conn = self.connection.create_connection()
        c = conn.cursor()

        if prefix:
            like_pattern = f"{prefix}%"
            c.execute(
                """
                SELECT DISTINCT instrument
                FROM instruments
                WHERE instrument LIKE ? ESCAPE '\\'
                COLLATE NOCASE
                ORDER BY instrument ASC
                LIMIT ?
                """,
                (like_pattern, limit)
            )
        else:
            c.execute(
                """
                SELECT DISTINCT instrument
                FROM instruments
                ORDER BY instrument ASC
                LIMIT ?
                """,
                (limit,)
            )

        rows = c.fetchall()
        conn.close()

        return [row[0] for row in rows]
