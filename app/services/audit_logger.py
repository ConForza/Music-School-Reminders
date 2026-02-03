import json
from datetime import datetime

class AuditLogger:
    def __init__(self, filepath: str = "audit.log"):
        self.filepath = filepath

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

        with open(self.filepath, "a") as f:
            f.write(json.dumps(record) + "\n")

    def status(self, errors):
        return "error" if errors else "ok"