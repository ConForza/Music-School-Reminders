from app.persistence.sqlite.audit_repository import AuditRepository
import json
from datetime import datetime

class AuditLogger:
    def __init__(self):
        self.audit_repository = AuditRepository()

    def log(self, command_request, result):
        """
        command_request: CommandRequest
        result: CommandResult
        """
        record = {
            "timestamp": datetime.now().isoformat(),
            "command": command_request.command,
            "source_id": command_request.source_id,
            "args": command_request.args,
            "result_type": result.type_,
            "routing": result.routing,
            "errors": result.errors,
            "status": self.status(result.errors)
        }

        self.audit_repository.save(record)

    def status(self, errors):
        return "error" if errors else "ok"