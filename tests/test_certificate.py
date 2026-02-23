from app.models.certificate import Certificate
from app.models.lesson import Lesson


class TestCertificate:

    lesson = Lesson(
        id_=1,
        date_raw="2026-02-23",
        type_="Piano lessons",
        category="piano",
        duration=30,
        payment="yes",
        appointment_type_id=5240856,
        certificate_code=None
    )

    def test_valid_certificate(self):

        certificate = Certificate(
            order_id=1,
            certificate_name="piano",
            expiration_date_raw="2026-03-04",
            remaining_minutes=30,
            appointment_type_ids=[5240856, 5240916]
        )
        assert certificate.can_apply_to(self.lesson)

    def test_expired_certificate(self):

        certificate = Certificate(
            order_id=1,
            certificate_name="piano",
            expiration_date_raw="2025-09-12",
            remaining_minutes=30,
            appointment_type_ids=[5240856, 5240916]
        )
        assert not certificate.can_apply_to(self.lesson)

    def test_invalid_appointment_ids(self):

        certificate = Certificate(
            order_id=1,
            certificate_name="piano",
            expiration_date_raw="2026-09-12",
            remaining_minutes=30,
            appointment_type_ids=[4512455, 4432451]
        )
        assert not certificate.can_apply_to(self.lesson)

    def test_no_remaining_minutes(self):

        certificate = Certificate(
            order_id=1,
            certificate_name="piano",
            expiration_date_raw="2026-09-12",
            remaining_minutes=0,
            appointment_type_ids=[5240856, 5240916]
        )
        assert not certificate.can_apply_to(self.lesson)
