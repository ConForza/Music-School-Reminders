from app.persistence.sqlite.staff_repository import StaffRepository
from app.services.daily_runner_service import DailyRunnerService
from app.services.certificate_service import CertificateService
from app.services.invoice_service import InvoiceService
from app.services.appointment_service import AppointmentService
from app.services.acuity_service import fetch_certificates_for_student
from app.services.audit_logger import AuditLogger
from app.models.student import Student
from app.persistence.sqlite.instrument_repository import InstrumentRepository


class CommandExecutor:

    def __init__(self):
        self.staff_repository = StaffRepository()
        self.runner = DailyRunnerService()
        self.certificate = CertificateService()
        self.invoice = InvoiceService()
        self.appointments = AppointmentService()
        self.audit_logger = AuditLogger()
        self.instrument_repository = InstrumentRepository()

    def run_all_staff(self, source, user_id, preview: bool = False):
        staff_members = self.staff_repository.get_all_staff()
        return self.runner.run_daily(staff_members, source=source, preview=preview)

    def generate_invoice(self, staff_id, date_from, date_to, source, user_id, preview: bool = False):
        return self.invoice.generate_invoice(
            staff_id=staff_id,
            date_from=date_from,
            date_to=date_to,
            source=source,
            preview=preview
        )

    def remaining_lessons(self, student_email, instrument, source, user_id, preview: bool = False):
        student = Student(first_name="", surname="", email=student_email)
        fetch_certificates_for_student(student)
        appt_type_ids = self.instrument_repository.get_in_person_appointment_type_ids(instrument)

        return self.certificate.remaining_lessons(
            student=student,
            instrument=instrument,
            appt_type_ids=appt_type_ids,
            source=source
        )

    def create_block(self, staff_id, student_email, lesson_duration, quantity, instrument, source, user_id, preview: bool = False):
        return self.certificate.create_block(
            staff_id=staff_id,
            student_email=student_email,
            lesson_duration=lesson_duration,
            quantity=quantity,
            source=source,
            preview=preview
        )

    def delete_all_lessons(self, staff_id, date_from, date_to, source, user_id, preview: bool = False):
        return self.appointments.delete_all_lessons(
            staff_id=staff_id,
            date_from=date_from,
            date_to=date_to,
            source=source,
            preview=preview
        )

    def delete_student_lessons(self, staff_id, student_email, date_from, date_to, instrument, source, user_id,
                               preview: bool = False):
        return self.appointments.delete_student_lessons(
            staff_id=staff_id,
            student_email=student_email,
            date_from=date_from,
            date_to=date_to,
            source=source,
            preview=preview
        )

    def audit_recent(self, source, user_id, limit: int = 5, preview: bool = False):
        return self.audit_logger.recent_executions(limit=limit, source=source)

    def audit_errors(self, source, user_id, limit: int = 5, preview: bool = False):
        return self.audit_logger.recent_errors(limit=limit, source=source)

    def audit_mine(self, source, user_id, limit: int = 5, preview: bool = False):
        return self.audit_logger.recent_for_user(limit=limit, user_id=user_id, source=source)
