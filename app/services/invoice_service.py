from app.models.command_result import CommandResult
from app.services.acuity_service import fetch_students_for_staff, fetch_certificates_for_student
from app.persistence.sqlite.staff_repository import StaffRepository
from app.services.certificate_service import CertificateService
from app.persistence.sqlite.price_repository import PriceRepository


class InvoiceService:

    def __init__(self):
        self.staff_repository = StaffRepository()
        self.price_repository = PriceRepository()
        self.certificate_service = CertificateService()

    def generate_invoice(self, staff_id: int, date_from, date_to, source, preview: bool = False):
        price_list = self.price_repository.get_invoice_values()
        errors = []
        lessons_to_add = []
        total_amount = 0
        staff_member = self.staff_repository.get_staff_record(staff_id)
        try:
            students = fetch_students_for_staff(staff_member, date_from, date_to)
            for student in students:
                fetch_certificates_for_student(student)
                self.certificate_service.apply_certificates_for_student(student, preview=preview)
                for lesson in student.lessons:
                    if lesson.is_taster():
                        lesson_cut = price_list["taster"]
                    elif lesson.duration == 60:
                        lesson_cut = price_list["60min"]
                    else:
                        lesson_cut = price_list["30min"]

                    total_amount += lesson_cut

                    lessons_to_add.append(
                        {
                            "name": f"{student.first_name} {student.surname}",
                            "duration": lesson.duration,
                            "lesson_cut": lesson_cut,
                            "lesson_paid": lesson.is_paid()
                        }
                    )

        except Exception as e:
            errors.append(f"{staff_member.name}: {str(e)}")

        routing = {
            "target": "admin"
        }

        return CommandResult(
            type_="GENERATE_INVOICE",
            content={
                "date_from": date_from,
                "date_to": date_to,
                "staff_id": staff_id,
                "lessons_to_add": lessons_to_add,
                "total_amount": total_amount,
                "preview": preview
            },
            errors=errors,
            routing=routing,
            source=source
        )