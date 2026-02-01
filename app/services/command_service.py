from app.services.staff_service import StaffService
from app.services.daily_runner_service import DailyRunnerService
from app.models.command_result import CommandResult
from services.certificate_service import CertificateService
from services.invoice_service import InvoiceService


class CommandService:

    def __init__(self):
        self.staff_service = StaffService()
        self.runner = DailyRunnerService()
        self.certificate = CertificateService()
        self.invoice = InvoiceService()


    def receive_command(self, command_request):
        args = command_request.args
        if command_request.command == "run_all_staff":
            return self.run_all_staff(preview=args["preview"])
        elif command_request.command == "remaining_lessons":
            if args.get("student_email"):
                return self.certificate.remaining_lessons(student_email=args["student_email"], source=command_request.source_id)
            else:
                return CommandResult(type_=command_request.command, errors=["Argument missing: 'student_email'."])
        elif command_request.command == "generate_invoice":
            required_args = ["staff_id", "date_from", "date_to"]
            errors = []
            for arg in required_args:
                if arg not in args:
                    errors.append(f"Argument missing: '{arg}'")

            if len(errors) > 0:
                return CommandResult(type_=command_request.command, errors=errors)
            else:
                return self.invoice.generate_invoice(
                    staff_id=args.staff_id,
                    date_from=args.date_from,
                    date_to=args.date_to,
                    preview=args.preview
                )
        else:
            return CommandResult(type_=command_request.command, errors=["Invalid command."])

    def run_all_staff(self, preview=False):
        staff_members = self.staff_service.get_all_staff()
        return self.runner.run_daily(staff_members, preview=preview)

    def run_staff_by_discord_id(self, discord_id, preview=False):
        staff = self.staff_service.get_staff_by_discord_id(discord_id)

        if staff is None:
            return CommandResult(
                type_="RUN_STAFF",
                content={},
                errors=[f"No staff found for discord id {discord_id}"],
                routing={"target": "admin"},
                source=discord_id
            )

        return self.runner.run_daily([staff], preview=preview)
