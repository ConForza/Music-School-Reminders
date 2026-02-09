from app.persistence.sqlite.connection import Connection
import json


class AuditRepository:

    def __init__(self):
        self.connection = Connection()
        self.connection.create_table()

    def save(self, record: dict) -> None:
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
                      record["timestamp"],
                      record["command"],
                      record["source_id"],
                      json.dumps(record["args"]),
                      record["result_type"],
                      json.dumps(record.get("routing")) if record.get("routing") is not None else None,
                      json.dumps(record.get("errors")) if record.get("errors") is not None else None,
                      record["status"]
                  )
                  )
        conn.commit()
        conn.close()
