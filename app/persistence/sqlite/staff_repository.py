from app.persistence.sqlite.connection import Connection
from app.models.staff import Staff

class StaffRepository:

    def __init__(self):
        self.connection = Connection()

    def get_by_user_id(self, user_id: int) -> int | None:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM staff WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        conn.close()

        if row is None:
            return None

        return row[0]

    def get_name_by_staff_id(self, staff_id: int) -> str | None:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("SELECT first_name FROM staff WHERE id = ?", (staff_id,))
        row = c.fetchone()
        conn.close()

        if row is None:
            return None

        return row[0]

    def get_staff_calendar_id(self, staff_id) -> int:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("SELECT acuity_calendar_id FROM staff WHERE id = ?", (staff_id,))
        row = c.fetchone()
        conn.close()

        if row is None:
            return None

        return row[0]

    def get_all_staff(self) -> list[Staff]:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, user_id, first_name, surname, role, acuity_calendar_id
            FROM staff
            ORDER BY surname, first_name
        """)
        rows = c.fetchall()
        conn.close()
        return [
            Staff(
                id_=r["id"],
                user_id=r["user_id"],
                first_name=r["first_name"],
                surname=r["surname"],
                role=r["role"],
                acuity_calendar_id=r["acuity_calendar_id"],
            )
            for r in rows
        ]

    def get_staff_record(self, staff_id) -> Staff:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("""
            SELECT id, user_id, first_name, surname, role, acuity_calendar_id
            FROM staff
            WHERE id = ?
        """, (staff_id,))
        r = c.fetchone()
        conn.close()
        return (
            Staff(
                id_=r["id"],
                user_id=r["user_id"],
                first_name=r["first_name"],
                surname=r["surname"],
                role=r["role"],
                acuity_calendar_id=r["acuity_calendar_id"]
            )
        )