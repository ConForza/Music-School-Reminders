from app.persistence.sqlite.connection import Connection
from app.models.command_execution import CommandExecution
from typing import List
import json


class AuditRepository:

    def __init__(self):
        self.connection = Connection()
        self.connection.create_tables()

    def save(self, execution: CommandExecution) -> None:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("""
                  INSERT INTO audit_logs (user_id,
                                          timestamp,
                                          command,
                                          source_id,
                                          args,
                                          result_type,
                                          routing,
                                          errors,
                                          status)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                  """,
                  (
                      execution.user_id,
                      execution.timestamp,
                      execution.command,
                      execution.source_id,
                      json.dumps(execution.args),
                      execution.result_type,
                      json.dumps(execution.routing) if execution.routing is not None else None,
                      json.dumps(execution.errors),
                      execution.status,
                  )
                  )
        conn.commit()
        conn.close()

    def get_recent(self, limit: int = 20) -> List[CommandExecution]:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute("SELECT * FROM audit_logs ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        executions: List[CommandExecution] = []
        for row in rows:
            (
                id_,
                user_id,
                timestamp,
                command,
                source_id,
                args,
                result_type,
                routing,
                errors,
                status
            ) = row

            executions.append(CommandExecution(
                id=id_,
                user_id=user_id,
                timestamp=timestamp,
                command=command,
                source_id=source_id,
                args=json.loads(args),
                result_type=result_type,
                routing=json.loads(routing) if routing is not None else None,
                errors=json.loads(errors),
                status=status,
            ))

        return executions

    def get_recent_for_user(self, user_id: int, limit: int = 20) -> List[CommandExecution]:
        conn = self.connection.create_connection()
        c = conn.cursor()
        c.execute(
            """
            SELECT * FROM audit_logs
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (user_id, limit)
        )
        rows = c.fetchall()
        conn.close()

        executions = []
        for row in rows:
            (
                id_,
                user_id_fk,
                timestamp,
                command,
                source_id,
                args,
                result_type,
                routing,
                errors,
                status,
            ) = row

            executions.append(CommandExecution(
                id=id_,
                user_id=user_id_fk,
                timestamp=timestamp,
                command=command,
                source_id=source_id,
                args=json.loads(args),
                result_type=result_type,
                routing=json.loads(routing) if routing is not None else None,
                errors=json.loads(errors),
                status=status,
            ))

        return executions
