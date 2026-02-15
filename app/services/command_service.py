from app.models.command_result import CommandResult
from app.models.command_definition import CommandDefinition
from app.services.command_executor import CommandExecutor
from app.services.audit_logger import AuditLogger
from app.persistence.sqlite.user_repository import UserRepository
from app.persistence.sqlite.staff_repository import StaffRepository


class CommandService:

    def __init__(self):
        self.executor = CommandExecutor()
        self.audit_logger = AuditLogger()
        self.user_repository = UserRepository()
        self.staff_repository = StaffRepository()

        self.registry = {
            "run_all_staff": CommandDefinition(
                required_args=[],
                optional_args=[],
                handler=self.executor.run_all_staff,
                access="admin_only"
            ),
            "remaining_lessons": CommandDefinition(
                required_args=["student_email"],
                optional_args=[],
                handler=self.executor.remaining_lessons,
                access="staff_or_admin"
            ),
            "generate_invoice": CommandDefinition(
                required_args=["staff_id", "date_from", "date_to"],
                optional_args=[],
                handler=self.executor.generate_invoice,
                access="staff_self_or_admin"
            ),
            "create_block": CommandDefinition(
                required_args=["staff_id", "student_email", "lesson_duration", "quantity"],
                optional_args=[],
                handler=self.executor.create_block,
                access="staff_self_or_admin"
            ),
            "delete_all_lessons": CommandDefinition(
                required_args=["staff_id", "date_from", "date_to"],
                optional_args=[],
                handler=self.executor.delete_all_lessons,
                access="staff_self_or_admin"
            ),
            "delete_student_lessons": CommandDefinition(
                required_args=["staff_id", "student_email", "date_from", "date_to"],
                optional_args=[],
                handler=self.executor.delete_student_lessons,
                access="staff_self_or_admin"
            ),
            "audit_recent": CommandDefinition(
                required_args=[],
                optional_args=["limit"],
                handler=self.executor.audit_recent,
                access="admin_only"
            ),
            "audit_errors": CommandDefinition(
                required_args=[],
                optional_args=["limit"],
                handler=self.executor.audit_errors,
                access="admin_only"
            ),
            "audit_mine": CommandDefinition(
                required_args=[],
                optional_args=["limit"],
                handler=self.executor.audit_mine,
                access="staff_or_admin"
            )
        }

    def _error_result(self, command_name, message, context, target="staff"):
        return CommandResult(
            type_=command_name,
            errors=[message],
            routing={"target": target},
            source=context["source_id"]
        )

    def _get_caller_context(self, command_request):
        user_id = command_request.principal_id

        is_admin = False
        if user_id is not None:
            user = self.user_repository.get_is_admin_by_id(user_id)
            is_admin = bool(user)

        return {
            "is_admin": is_admin,
            "source_id": command_request.source_id,
            "user_id": user_id
        }

    def _check_access(self, command_name, definition, args, context):
        access = definition.access

        if access == "admin_only" and not context["is_admin"]:
            return self._error_result(
                command_name,
                "You do not have permission to run this command.",
                context
            )

        if access == "staff_or_admin":
            if context.get("user_id") is None:
                return self._error_result(
                    command_name,
                    "Permission error: user not found",
                    context
                )

        if access == "staff_self_or_admin" and not context["is_admin"]:
            staff_id_arg = args.get("staff_id")
            if staff_id_arg is None:
                return self._error_result(command_name, "Argument missing: 'staff_id'", context)
            try:
                staff_id_arg = int(staff_id_arg)
            except (TypeError, ValueError):
                return self._error_result(
                    command_name,
                    "Argument 'staff_id' must be an integer staff id",
                    context
                )

            user_id = context.get("user_id")

            if user_id is None:
                return self._error_result(
                    command_name,
                    "Permission error: user not found",
                    context
                )

            staff = self.staff_repository.get_by_user_id(user_id)

            if staff is None or staff != staff_id_arg:
                return self._error_result(
                    command_name,
                    "Permission error: staff_id does not belong to you",
                    context
                )

        return None

    def validate_args(self, command, args, required_args: list):
        errors = []
        for arg in required_args:
            if arg not in args or args[arg] is None:
                errors.append(f"Argument missing: '{arg}'")
                continue

            if isinstance(args[arg],str) and args[arg].strip() == "":
                errors.append(f"Argument missing: '{arg}'")

        if errors:
            return CommandResult(type_=command, errors=errors)

        return None

    def _coerce_optional_args(self, command, definition, args, context):
        opt_args = {k: v for k, v in args.items() if k in definition.optional_args}

        if "limit" in definition.optional_args:
            if "limit" in opt_args:
                try:
                    opt_args["limit"] = int(opt_args["limit"])
                except (TypeError, ValueError):
                    return None, self._error_result(
                        command,
                        "Argument 'limit' must be an integer",
                        context
                    )
            else:
                opt_args["limit"] = 5

            opt_args["limit"] = max(1, min(opt_args["limit"], 50))

        return opt_args, None

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
            self.audit_logger.log(command_request, access_error)
            return access_error

        opt_args, opt_error = self._coerce_optional_args(command, definition, args, context)
        if opt_error:
            self.audit_logger.log(command_request, opt_error)
            return opt_error

        preview = args.get("preview", definition.default_preview)

        result = definition.handler(
            **{k: args[k] for k in definition.required_args},
            **opt_args,
            user_id=context["user_id"],
            source=context["source_id"],
            preview=preview
        )

        self.audit_logger.log(command_request, result)
        return result
