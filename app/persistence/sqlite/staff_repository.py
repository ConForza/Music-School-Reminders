from app.persistence.sqlite.connection import Connection

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