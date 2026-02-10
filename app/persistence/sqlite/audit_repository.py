from app.persistence.sqlite.connection import Connection
from models.command_execution import CommandExecution
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
                  INSERT INTO audit_logs (timestamp,
                                          command,
                                          source_id,
                                          args,
                                          result_type,
                                          routing,
                                          errors,
                                          status)
                  VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                  """,
                  (
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
        results = c.fetchall()
        conn.close()
        executions: List[CommandExecution] = []
        for result in results:
            (
                id_,
                timestamp,
                command,
                source_id,
                args,
                result_type,
                routing,
                errors,
                status
            ) = result

            executions.append(CommandExecution(
                id=id_,
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
