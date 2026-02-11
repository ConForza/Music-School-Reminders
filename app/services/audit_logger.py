from app.persistence.sqlite.audit_repository import AuditRepository
from models.command_execution import CommandExecution
from datetime import datetime
from typing import List

from persistence.sqlite.user_repository import UserRepository


class AuditLogger:
    def __init__(self):
        self.audit_repository = AuditRepository()
        self.user_repository = UserRepository()

    def log(self, command_request, result):
        user_id = self.user_repository.find_id_by_discord_id(command_request.source_id)

        command_execution = CommandExecution(
            id=None,
            user_id=user_id,
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

    def recent_executions(self, limit: int = 20) -> List[CommandExecution]:
        return self.audit_repository.get_recent(limit)

    def recent_errors(self, limit: int = 20) -> List[CommandExecution]:
        return [
            e for e in self.audit_repository.get_recent(limit * 2) if e.status == "error"
        ][:limit]

    def recent_for_user(self, user_id: int, limit: int = 20) -> List[CommandExecution]:
        return self.audit_repository.get_recent_for_user(user_id, limit)