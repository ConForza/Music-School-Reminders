from app.models.payment import Payment
from app.models.lesson import Lesson
from app.models.staff import Staff
from app.models.student import Student
import app.services.acuity_service as acuity_service
import app.services.invoice_service as invoice_service


class TestInvoiceService:

    def set_up_student_staff_and_lessons(self):
        lesson1 = Lesson(
            id_=1,
            date_raw="2026-02-23",
            type_="Piano lessons",
            category="piano",
            duration=30,
            payment=Payment(is_paid_raw="yes"),
            appointment_type_id=5240856,
            certificate_code=None
        )

        lesson2 = Lesson(
            id_=2,
            date_raw="2026-02-23",
            type_="Piano lessons",
            category="piano",
            duration=60,
            payment=Payment(is_paid_raw="yes"),
            appointment_type_id=5240856,
            certificate_code=None
        )

        lesson3 = Lesson(
            id_=3,
            date_raw="2026-02-23",
            type_="Piano lessons",
            category="piano",
            duration=30,
            payment=Payment(is_paid_raw="yes"),
            appointment_type_id=5240856,
            certificate_code="TASTER"
        )

        student = Student(
            first_name="Joe",
            surname="Bloggs",
            email="joe@bloggs.com"
        )

        student.add_lesson(lesson1)
        student.add_lesson(lesson2)
        student.add_lesson(lesson3)

        staff = Staff(
            id_=1,
            user_id=123,
            first_name="John",
            surname="Smith",
            role="Teacher",
            acuity_calendar_id="123456",
            discord_id=None
        )

        return student, staff

    def test_totals_and_lessons(self, monkeypatch):
        student, staff = self.set_up_student_staff_and_lessons()
        invoice = invoice_service.InvoiceService()

        def fake_fetch_students_appointments(staff, date_from, date_to):
            return [student]

        def fake_fetch_certificates_for_student(student_arg):
            return None

        def fake_get_invoice_values():
            return {"30min": 10.0, "60min": 15.0, "taster": 8.0}

        def fake_get_staff_record(self, staff_id):
            return staff


        monkeypatch.setattr(invoice_service, "fetch_students_for_staff", fake_fetch_students_appointments)
        monkeypatch.setattr(acuity_service, "fetch_certificates_for_student", fake_fetch_certificates_for_student)
        monkeypatch.setattr(invoice_service.PriceRepository, "get_invoice_values", staticmethod(fake_get_invoice_values))
        monkeypatch.setattr(invoice_service.StaffRepository, "get_staff_record", fake_get_staff_record)

        result = invoice.generate_invoice(1, "2026-02-23", "2026-02-23", source=123, preview=False)


        assert result.type_ == "GENERATE_INVOICE"
        assert len(result.errors) == 0
        assert len(result.content["lessons_to_add"]) == 3
        lessons = result.content["lessons_to_add"]
        assert [l["duration"] for l in lessons] == [30, 60, 30]
        assert [l["lesson_cut"] for l in lessons] == [10.0, 15.0, 8.0]
        assert result.content["total_amount"] == 10.0 + 15.0 + 8.0


    def test_preview(self, monkeypatch):
        student, staff = self.set_up_student_staff_and_lessons()
        invoice = invoice_service.InvoiceService()

        def fake_fetch_students_appointments(staff, date_from, date_to):
            return [student]

        def fake_fetch_certificates_for_student(student_arg):
            return None

        def fake_get_invoice_values():
            return {"30min": 10.0, "60min": 15.0, "taster": 8.0}

        def fake_get_staff_record(self, staff_id):
            return staff


        monkeypatch.setattr(invoice_service, "fetch_students_for_staff", fake_fetch_students_appointments)
        monkeypatch.setattr(acuity_service, "fetch_certificates_for_student", fake_fetch_certificates_for_student)
        monkeypatch.setattr(invoice_service.PriceRepository, "get_invoice_values", staticmethod(fake_get_invoice_values))
        monkeypatch.setattr(invoice_service.StaffRepository, "get_staff_record", fake_get_staff_record)

        result = invoice.generate_invoice(1, "2026-02-23", "2026-02-23", source=123, preview=True)

        lessons = result.content["lessons_to_add"]
        assert result.content["preview"] == True
        assert [l["duration"] for l in lessons] == [30, 60, 30]
        assert [l["lesson_cut"] for l in lessons] == [10.0, 15.0, 8.0]
        assert result.content["total_amount"] == 10.0 + 15.0 + 8.0


    def test_raise_exception_in_fetch_students_for_staff(self, monkeypatch):
        student, staff = self.set_up_student_staff_and_lessons()
        invoice = invoice_service.InvoiceService()


        def fake_fetch_students_appointments(staff, date_from, date_to):
            raise AssertionError("BIG FAKE API ERROR")

        def fake_fetch_certificates_for_student(student_arg):
            return None

        def fake_get_invoice_values():
            return {"30min": 10.0, "60min": 15.0, "taster": 8.0}

        def fake_get_staff_record(self, staff_id):
            return staff

        monkeypatch.setattr(invoice_service, "fetch_students_for_staff", fake_fetch_students_appointments)
        monkeypatch.setattr(acuity_service, "fetch_certificates_for_student", fake_fetch_certificates_for_student)
        monkeypatch.setattr(invoice_service.PriceRepository, "get_invoice_values",
                            staticmethod(fake_get_invoice_values))
        monkeypatch.setattr(invoice_service.StaffRepository, "get_staff_record", fake_get_staff_record)

        result = invoice.generate_invoice(1, "2026-02-23", "2026-02-23", source=123, preview=False)

        assert result.type_ == "GENERATE_INVOICE"
        assert len(result.errors) == 1
        assert result.errors[0] == f"John Smith: BIG FAKE API ERROR"
        lessons = result.content["lessons_to_add"]
        assert len(lessons) == 0
        assert result.content["total_amount"] == 0
