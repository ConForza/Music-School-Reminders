from app.persistence.sqlite.connection import Connection

class PriceRepository:

    def __init__(self):
        self.connection = Connection()

    def get_invoice_values(self) -> dict[str, float]:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute(
            "SELECT lesson_type, staff_cut FROM prices"
        )
        rows = c.fetchall()
        conn.close()

        return {r["lesson_type"]: float(r["staff_cut"] / 100.0) for r in rows}