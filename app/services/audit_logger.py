from app.persistence.sqlite.audit_repository import AuditRepository
from app.models.command_execution import CommandExecution
from app.models.command_result import CommandResult
from app.persistence.sqlite.user_repository import UserRepository
from datetime import datetime


class AuditLogger:
    def __init__(self):
        self.audit_repository = AuditRepository()
        self.user_repository = UserRepository()

    def log(self, command_request, result):
        command_execution = CommandExecution(
            id=None,
            user_id=command_request.principal_id,
            timestamp=datetime.now().isoformat(),
            command=command_request.command,
            source_id=command_request.source_id,
            args=command_request.args,
            result_type=result.type_,
            routing=result.routing,
            errors=result.errors,
            status=self.status(result.errors)
        )

        self.audit_repository.save(command_execution)

    def status(self, errors):
        return "error" if errors else "ok"

    def recent_executions(self, source, limit: int = 20):
        results = self.audit_repository.get_recent(limit)
        routing = {
            "target": "admin"
        }

        return CommandResult(
            type_="AUDIT_RECENT",
            content={
                "results": results
            },
            routing=routing,
            errors=None,
            source=source
        )

    def recent_errors(self, source, limit: int = 20):
        results = [
            e for e in self.audit_repository.get_recent(limit * 2) if e.status == "error"
        ][:limit]

        routing = {
            "target": "admin"
        }

        return CommandResult(
            type_="AUDIT_ERRORS",
            content={
                "results": results
            },
            routing=routing,
            errors=None,
            source=source
        )

    def recent_for_user(self, source, user_id, limit: int = 20):
        results = self.audit_repository.get_recent_for_user(user_id, limit)
        routing = {
            "target": "staff"
        }
        return CommandResult(
            type_="AUDIT_MINE",
            content={
                "results": results
            },
            routing=routing,
            errors=None,
            source=source
        )
