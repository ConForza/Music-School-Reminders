from app.services.staff_service import StaffService
from app.services.daily_runner_service import DailyRunnerService
from app.services.certificate_service import CertificateService
from app.services.invoice_service import InvoiceService
from app.services.appointment_service import AppointmentService
from app.models.command_result import CommandResult

class CommandExecutor:

    def __init__(self):
        self.staff_service = StaffService()
        self.runner = DailyRunnerService()
        self.certificate = CertificateService()
        self.invoice = InvoiceService()
        self.appointments = AppointmentService()

    def run_all_staff(self, source, preview: bool=False):
        staff_members = self.staff_service.get_all_staff()
        return self.runner.run_daily(staff_members, source=source, preview=preview)

    def generate_invoice(self, staff_id, date_from, date_to, source, preview: bool=False):
        return self.invoice.generate_invoice(
            staff_id=staff_id,
            date_from=date_from,
            date_to=date_to,
            source=source,
            preview=preview
        )

    def remaining_lessons(self, student_email, source, preview: bool=False):
        return self.certificate.remaining_lessons(
            student_email=student_email,
            source=source
        )

    def create_block(self, staff_id, student_email, lesson_duration, quantity, source, preview: bool=False):
        return self.certificate.create_block(
            staff_id=staff_id,
            student_email=student_email,
            lesson_duration=lesson_duration,
            quantity=quantity,
            source=source
        )

    def delete_all_lessons(self, staff_id, date_from, date_to, source, preview: bool=False):
        return self.appointments.delete_all_lessons(
            staff_id=staff_id,
            date_from=date_from,
            date_to=date_to,
            source=source
        )

    def delete_student_lessons(self, staff_id, student_email, date_from, date_to, source, preview: bool=False):
        return self.appointments.delete_student_lessons(
            staff_id=staff_id,
            student_email=student_email,
            date_from=date_from,
            date_to=date_to,
            source=source
        )

    def run_staff_by_discord_id(self, discord_id, preview: bool=False):
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