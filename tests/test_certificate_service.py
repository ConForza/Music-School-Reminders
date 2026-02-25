from app.services.certificate_service import CertificateService
from app.models.lesson import Lesson
from app.models.payment import Payment
from app.models.certificate import Certificate
import app.services.acuity_service as acuity_service
from app.models.student import Student

class TestCertificateService:

    certificate_service = CertificateService()

    def make_student_with_lesson_and_certs(self):
        lesson1 = Lesson(
            id_=1,
            date_raw="2026-02-23",
            type_="Piano lessons",
            category="piano",
            duration=30,
            payment=Payment(is_paid_raw="no"),
            appointment_type_id=5240856,
            certificate_code=None
        )

        lesson2 = Lesson(
            id_=2,
            date_raw="2026-02-23",
            type_="Piano lessons",
            category="piano",
            duration=30,
            payment=Payment(is_paid_raw="no"),
            appointment_type_id=5240856,
            certificate_code=None
        )

        student = Student(
            first_name="Joe",
            surname="Bloggs",
            email="joe@bloggs.com"
        )

        cert1 = Certificate(
            order_id=1,
            certificate_name="piano",
            expiration_date_raw="2026-03-04",
            remaining_minutes=30,
            appointment_type_ids=[5240856, 5240916]
        )

        cert2 = Certificate(
            order_id=2,
            certificate_name="piano",
            expiration_date_raw="2026-05-04",
            remaining_minutes=30,
            appointment_type_ids=[5240856, 5240916]
        )

        cert3 = Certificate(
            order_id=3,
            certificate_name="piano",
            expiration_date_raw="2026-02-27",
            remaining_minutes=30,
            appointment_type_ids=[5240856, 5240916]
        )

        cert4 = Certificate(
            order_id=4,
            certificate_name="piano",
            expiration_date_raw="2026-02-28",
            remaining_minutes=0,
            appointment_type_ids=[5240856, 5240916]
        )

        cert5 = Certificate(
            order_id=5,
            certificate_name="piano",
            expiration_date_raw="2026-02-24",
            remaining_minutes=30,
            appointment_type_ids=[34564536, 3456354631]
        )

        student.add_certificate(cert1)
        student.add_certificate(cert2)
        student.add_certificate(cert3)
        student.add_certificate(cert4)
        student.add_certificate(cert5)
        student.add_lesson(lesson1)
        student.add_lesson(lesson2)

        return student

    def test_selects_earliest_expiring_valid_certificate(self):

        student = self.make_student_with_lesson_and_certs()

        assert self.certificate_service.select_certificate_for_lesson(student, student.lessons[0]).order_id == 3


    def test_preview_mode_does_not_mutate_state(self):
        student = self.make_student_with_lesson_and_certs()

        results = self.certificate_service.apply_certificates_for_student(student, preview=True)

        assert all(result.status == "applied" for result in results)
        assert student.lessons[0].is_unpaid()
        assert student.lessons[1].is_unpaid()

    def test_api_failure_records_error_and_does_not_make_paid(self, monkeypatch):
        student = self.make_student_with_lesson_and_certs()

        def fake_apply(order_id, lesson_id, preview):
            return False, "API ERROR"

        monkeypatch.setattr(acuity_service, "apply_certificate_to_lesson", fake_apply)

        results = self.certificate_service.apply_certificates_for_student(student, preview=False)

        assert len(results) == 2
        r=results[0]
        assert r.status == "API ERROR"
        assert r.certificate_id == student.certificates[2].order_id
        assert not student.lessons[0].is_paid()

    def test_no_valid_cert_returns_no_valid_status(self, monkeypatch):
        student = Student("Joe", "Bloggs", "joe@bloggs.com")
        lesson = Lesson(
            id_=1,
            date_raw="2026-02-23",
            type_="Piano lessons",
            category="piano",
            duration=30,
            payment=Payment(is_paid_raw="no"),
            appointment_type_id=5240856,
            certificate_code=None
        )
        student.add_lesson(lesson)

        def fake_apply(order_id, lesson_id, preview):
            raise AssertionError("API should not be called with no valid certificates")

        monkeypatch.setattr(acuity_service, "apply_certificate_to_lesson", fake_apply)

        results = self.certificate_service.apply_certificates_for_student(student, preview=False)

        assert len(results) == 1
        r = results[0]
        assert r.status == "no_valid_certificate"