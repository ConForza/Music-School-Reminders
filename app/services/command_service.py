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
                handler=self.executor.run_all_staff
            ),
            "remaining_lessons": CommandDefinition(
                required_args=["student_email"],
                handler=self.executor.remaining_lessons
            ),
            "generate_invoice": CommandDefinition(
                required_args=["staff_id", "date_from", "date_to"],
                handler=self.executor.generate_invoice
            ),
            "create_block": CommandDefinition(
                required_args=["staff_id", "student_email", "lesson_duration", "quantity"],
                handler=self.executor.create_block
            ),
            "delete_all_lessons": CommandDefinition(
                required_args=["staff_id", "date_from", "date_to"],
                handler=self.executor.delete_all_lessons
            ),
            "delete_student_lessons": CommandDefinition(
                required_args=["staff_id", "student_email", "date_from", "date_to"],
                handler=self.executor.delete_student_lessons
            )
        }

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
        source = command_request.source_id

        if command not in self.registry:
            result = CommandResult(
                type_=command,
                errors=["Invalid command."]
            )
            self.audit_logger.log(command_request, result)
            return result

        definition = self.registry[command]

        error_result = self.validate_args(command, args, definition.required_args)
        if error_result:
            self.audit_logger.log(command_request, error_result)
            return error_result

        result = definition.handler(
            **{k: args[k] for k in definition.required_args},
            source=source,
            preview=args.get("preview", False)
        )

        self.audit_logger.log(command_request, result)
        return result

