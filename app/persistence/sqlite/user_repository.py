from app.persistence.sqlite.connection import Connection
import json
from typing import Optional, List

from models.command_execution import CommandExecution


class UserRepository:
    def __init__(self):
        self.connection = Connection()

    def find_id_by_discord_id(self, discord_id: str) -> Optional[int]:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE discord_id = ?", (discord_id,))
        row = c.fetchone()
        conn.close()

        if row is None:
            return None

        return row[0]
