from app.models.command_result import CommandResult
from app.models.command_definition import CommandDefinition
from app.services.command_executor import CommandExecutor
from app.services.audit_logger import AuditLogger


class CommandService:

    def __init__(self):
        self.executor = CommandExecutor()
        self.audit_logger = AuditLogger()

        self.registry = {
            "run_all_staff": CommandDefinition(
                required_args=[],
                handler=self.executor.run_all_staff,
                access="admin_only"
            ),
            "remaining_lessons": CommandDefinition(
                required_args=["student_email"],
                handler=self.executor.remaining_lessons,
                access="staff_or_admin"
            ),
            "generate_invoice": CommandDefinition(
                required_args=["staff_id", "date_from", "date_to"],
                handler=self.executor.generate_invoice,
                access="staff_self_or_admin"
            ),
            "create_block": CommandDefinition(
                required_args=["staff_id", "student_email", "lesson_duration", "quantity"],
                handler=self.executor.create_block,
                access="staff_self_or_admin"
            ),
            "delete_all_lessons": CommandDefinition(
                required_args=["staff_id", "date_from", "date_to"],
                handler=self.executor.delete_all_lessons,
                access="staff_self_or_admin"
            ),
            "delete_student_lessons": CommandDefinition(
                required_args=["staff_id", "student_email", "date_from", "date_to"],
                handler=self.executor.delete_student_lessons,
                access="staff_self_or_admin"
            )
        }

    def _get_caller_context(self, command_request):
        routing = command_request.routing or {}
        permissions = routing.get("permissions", [])
        is_admin = "Administrator" in permissions

        return {
            "is_admin": is_admin,
            "source_id": command_request.source_id
        }

    def _check_access(self, command_name, definition, args, context):
        access = definition.access

        if access == "admin_only" and not context["is_admin"]:
            return CommandResult(
                type_=command_name,
                errors=["You do not have permission to run this command."],
                routing={"target": "staff"},
                source=context["source_id"]
            )

        if access == "staff_self_or_admin" and not context["is_admin"]:
            staff_id_arg = args.get("staff_id")
            if staff_id_arg is None:
                return CommandResult(
                    type_=command_name,
                    errors=["Argument missing: 'staff_id'"],
                    routing={"target": "staff"},
                    source=context["source_id"]
                )

        return None

    def validate_args(self, command, args, required_args: list):
        errors = []
        for arg in required_args:
            if arg not in args:
                errors.append(f"Argument missing: '{arg}'")

        if len(errors) > 0:
            return CommandResult(type_=command, errors=errors)

        return None

    def receive_command(self, command_request):
        command = command_request.command
        args = command_request.args

        if command not in self.registry:
            result = CommandResult(
                type_=command,
                errors=["Invalid command."]
            )
            self.audit_logger.log(command_request, result)
            return result

        context = self._get_caller_context(command_request)
        definition = self.registry[command]

        error = self.validate_args(command, args, definition.required_args)
        if error:
            self.audit_logger.log(command_request, error)
            return error

        access_error = self._check_access(command, definition, args, context)
        if access_error:
            return access_error

        preview = args.get("preview", definition.default_preview)

        result = definition.handler(
            **{k: args[k] for k in definition.required_args},
            source=context["source_id"],
            preview=preview
        )

        self.audit_logger.log(command_request, result)
        return result

