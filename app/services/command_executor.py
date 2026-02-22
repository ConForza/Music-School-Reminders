from app.persistence.sqlite.staff_repository import StaffRepository
from app.services.daily_runner_service import DailyRunnerService
from app.services.certificate_service import CertificateService
from app.services.invoice_service import InvoiceService
from app.services.appointment_service import AppointmentService
from app.services.acuity_service import fetch_certificates_for_student, is_valid_email
from app.services.audit_logger import AuditLogger
from app.models.command_result import CommandResult
from app.models.student import Student
from app.persistence.sqlite.instrument_repository import InstrumentRepository
from datetime import datetime


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

    def generate_invoice(self, staff_id: int, date_from, date_to, source, user_id, preview: bool = False):
        routing = {"target": "staff"}
        try:
            date_from = datetime.strptime(date_from, "%d/%m/%y").strftime("%B %d, %Y")
            date_to = datetime.strptime(date_to, "%d/%m/%y").strftime("%B %d, %Y")
        except (TypeError, ValueError):
            return CommandResult(
                type_="GENERATE_INVOICE",
                content={},
                errors=["❌ Dates must be in the format dd/mm/yy"],
                routing=routing,
                source=source
            )

        return self.invoice.generate_invoice(
            staff_id=staff_id,
            date_from=date_from,
            date_to=date_to,
            source=source,
            preview=preview
        )

    def remaining_lessons(self, student_email, instrument, source, user_id, preview: bool = False):
        routing = {"target": "staff"}
        instrument = instrument.strip()
        student_email = student_email.strip().lower()

        if not is_valid_email(student_email):
            return CommandResult(
                type_="REMAINING_LESSONS",
                content={
                    "student_email": student_email,
                    "instrument": instrument,
                },
                errors=[
                    "❌ Student email does not exist on Acuity."
                ],
                routing=routing,
                source=source
            )

        if not self.instrument_repository.instrument_exists(instrument):
            return CommandResult(
                type_="REMAINING_LESSONS",
                content={
                    "student_email": student_email,
                    "instrument": instrument,
                },
                errors=[
                    "❌ Instrument not found. Please check your spelling."
                ],
                routing=routing,
                source=source
            )

        appt_type_ids = self.instrument_repository.get_in_person_appointment_type_ids(instrument)
        student = Student(first_name="", surname="", email=student_email)
        fetch_certificates_for_student(student)

        return self.certificate.remaining_lessons(
            student=student,
            instrument=instrument,
            appt_type_ids=appt_type_ids,
            routing=routing,
            source=source
        )

    def create_block(self, staff_id, student_email, lesson_duration, quantity, instrument, source, user_id, preview: bool = False):
        routing = {"target": "staff"}
        student_email = student_email.strip().lower()
        instrument = instrument.strip()
        try:
            lesson_duration_int = int(lesson_duration)
            quantity_int = int(quantity)
        except (TypeError, ValueError):
            return CommandResult(
                type_="CREATE_BLOCK",
                content={},
                errors=["❌ Lesson 'duration' and 'quantity' must be integers."],
                routing=routing,
                source=source
            )

        if not is_valid_email(student_email):
            return CommandResult(
                type_="CREATE_BLOCK",
                content={},
                errors=["❌ Student email does not exist on Acuity."],
                routing=routing,
                source=source
            )

        if lesson_duration_int not in (30, 60):
            return CommandResult(
                type_="CREATE_BLOCK",
                content={},
                errors=["❌ Lesson 'duration' must be either 30 or 60 minutes."],
                routing=routing,
                source=source
            )

        if quantity_int <= 0:
            return CommandResult(
                type_="CREATE_BLOCK",
                content={},
                errors=["❌ Quantity must be greater than zero."],
                routing=routing,
                source=source
            )

        if not self.instrument_repository.instrument_exists(instrument):
            return CommandResult(
                type_="CREATE_BLOCK",
                content={
                    "student_email": student_email,
                    "staff_id": staff_id,
                    "lesson_duration": lesson_duration_int,
                    "instrument": instrument,
                    "quantity": quantity_int,
                    "preview": preview
                },
                errors=[
                    "❌ Instrument not found. Please check your spelling."
                ],
                routing=routing,
                source=source
            )

        cert_code = self.instrument_repository.get_certificate_code(instrument, lesson_duration_int)
        if cert_code is None:
            return CommandResult(
                type_="CREATE_BLOCK",
                content={
                    "student_email": student_email,
                    "staff_id": staff_id,
                    "lesson_duration": lesson_duration_int,
                    "instrument": instrument,
                    "quantity": quantity_int,
                    "preview": preview
                },
                errors=[
                    f"❌ No certificate found for {instrument} {lesson_duration_int}min lessons. "
                    f"Please check the instruments table."
                ],
                routing=routing,
                source=source
            )

        return self.certificate.create_block(
            staff_id=staff_id,
            student_email=student_email,
            lesson_duration=lesson_duration_int,
            quantity=quantity_int,
            instrument=instrument,
            cert_code=cert_code,
            routing=routing,
            source=source,
            preview=preview
        )

    def delete_all_lessons(self, staff_id, date_from, date_to, source, user_id, preview: bool = False):
        routing = {"target": "staff"}
        try:
            date_from = datetime.strptime(date_from, "%d/%m/%y").strftime("%B %d, %Y")
            date_to = datetime.strptime(date_to, "%d/%m/%y").strftime("%B %d, %Y")
        except (TypeError, ValueError):
            return CommandResult(
                type_="DELETE_ALL_LESSONS",
                content={},
                errors=["❌ Dates must be in the format dd/mm/yy"],
                routing=routing,
                source=source
            )

        return self.appointments.delete_all_lessons(
            staff_id=staff_id,
            date_from=date_from,
            date_to=date_to,
            routing=routing,
            source=source,
            preview=preview
        )

    def delete_student_lessons(self, staff_id, student_email, date_from, date_to, source, user_id, instrument = None,
                               preview: bool = False):
        routing = {"target": "staff"}
        try:
            date_from = datetime.strptime(date_from, "%d/%m/%y").strftime("%B %d, %Y")
            date_to = datetime.strptime(date_to, "%d/%m/%y").strftime("%B %d, %Y")
        except (TypeError, ValueError):
            return CommandResult(
                type_="DELETE_STUDENT_LESSONS",
                content={},
                errors=["❌ Dates must be in the format dd/mm/yy"],
                routing=routing,
                source=source
            )

        student_email = student_email.strip().lower()
        if not is_valid_email(student_email):
            return CommandResult(
                type_="DELETE_STUDENT_LESSONS",
                content={},
                errors=["❌ Student email does not exist on Acuity."],
                routing=routing,
                source=source
            )

        if instrument:
            instrument = instrument.strip()
            if not self.instrument_repository.instrument_exists(instrument):
                return CommandResult(
                    type_="DELETE_STUDENT_LESSONS",
                    content={
                        "student_email": student_email,
                        "instrument": instrument,
                    },
                    errors=[
                        "❌ Instrument not found. Please check your spelling."
                    ],
                    routing=routing,
                    source=source
                )

        return self.appointments.delete_student_lessons(
            staff_id=staff_id,
            student_email=student_email,
            date_from=date_from,
            date_to=date_to,
            instrument=instrument,
            routing=routing,
            source=source,
            preview=preview
        )

    def audit_recent(self, source, user_id, limit: int = 5, preview: bool = False):
        return self.audit_logger.recent_executions(limit=limit, source=source)

    def audit_errors(self, source, user_id, limit: int = 5, preview: bool = False):
        return self.audit_logger.recent_errors(limit=limit, source=source)

    def audit_mine(self, source, user_id, limit: int = 5, preview: bool = False):
        return self.audit_logger.recent_for_user(limit=limit, user_id=user_id, source=source)
