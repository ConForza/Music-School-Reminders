from app.services.certificate_service import CertificateService
from app.models.lesson import Lesson
from app.models.payment import Payment
from app.models.certificate import Certificate
from app.models.student import Student

class TestCertificateService:

    certificate_service = CertificateService()

    def test_selects_earliest_expiring_valid_certificate(self):
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

        student = Student(
            first_name="Joe",
            surname="Bloggs",
            email="joe@bloggs.com"
        )

        student.add_lesson(lesson)

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

        assert self.certificate_service.select_certificate_for_lesson(student, lesson).order_id == 3


    def test_preview_mode_does_not_mutate_state(self):
        student = Student(
            first_name="Joe",
            surname="Bloggs",
            email="joe@bloggs.com"
        )

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

        cert = Certificate(
            order_id=1,
            certificate_name="piano",
            expiration_date_raw="2026-02-27",
            remaining_minutes=60,
            appointment_type_ids=[5240856, 5240916]
        )

        student.add_lesson(lesson1)
        student.add_lesson(lesson2)
        student.add_certificate(cert)

        results = self.certificate_service.apply_certificates_for_student(student, preview=True)

        assert all(result.status == "applied" for result in results)
        assert lesson1.is_unpaid()
        assert lesson2.is_unpaid()
