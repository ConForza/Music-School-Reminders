import app.services.acuity_service as acuity_service
from app.models.lesson_result import LessonResult
from app.models.command_result import CommandResult


class CertificateService:

    def select_certificate_for_lesson(self, student, lesson):

        valid_certificates = student.valid_certificates_for(lesson)

        if not valid_certificates:
            return None

        valid_certificates.sort(key=lambda c: c.expiration_date)

        return valid_certificates[0]

    def apply_certificates_for_student(self, student, preview):

        results = []
        total_minutes = sum(
            cert.remaining_minutes
            for cert in student.certificates
            if not cert.is_expired()
            and any(lesson.appointment_type_id in cert.appointment_type_ids
                    for lesson in student.unpaid_lessons())
        )

        for lesson in student.unpaid_lessons():
            certificate = self.select_certificate_for_lesson(student, lesson)
            if certificate is None:
                results.append(LessonResult(
                    lesson_id=lesson.id_,
                    lesson_date=lesson.date,
                    duration=lesson.duration,
                    status="no_valid_certificate"
                ))
                continue

            success, error = acuity_service.apply_certificate_to_lesson(
                certificate.order_id,
                lesson.id_,
                preview=preview
            )

            if success:
                total_minutes -= lesson.duration
                remaining_lessons = total_minutes // lesson.duration
                results.append(LessonResult(
                    lesson_id=lesson.id_,
                    lesson_date=lesson.date,
                    duration=lesson.duration,
                    status="applied",
                    certificate_id=certificate.order_id,
                    remaining_lessons=remaining_lessons
                ))
                continue
            else:
                results.append(LessonResult(
                    lesson_id=lesson.id_,
                    lesson_date=lesson.date,
                    duration=lesson.duration,
                    status=error,
                    certificate_id=certificate.order_id,
                ))
                continue

        return results

    def create_block(self, staff_id: int, student_email: str, lesson_duration: int, quantity: int, instrument: str,
                     cert_code: int, routing, source, preview: bool = False):

        success, error = acuity_service.create_certificates_for_student(cert_code, student_email, quantity, preview)
        if success:
            return CommandResult(
                type_="CREATE_BLOCK",
                content={
                    "student_email": student_email,
                    "staff_id": staff_id,
                    "lesson_duration": lesson_duration,
                    "instrument": instrument,
                    "quantity": quantity,
                    "preview": preview
                },
                errors=None,
                routing=routing,
                source=source
            )


        message = f"❌ Certificate creation failed: {error}." if error else "❌ Certificate creation failed for an unknown reason."

        return CommandResult(
            type_="CREATE_BLOCK",
            content={
                "student_email": student_email,
                "staff_id": staff_id,
                "lesson_duration": lesson_duration,
                "instrument": instrument,
                "quantity": quantity,
                "preview": preview
            },
            errors=[message],
            routing=routing,
            source=source
        )

    def remaining_lessons(self, student, instrument: str, appt_type_ids: dict, routing, source):

        id_30 = appt_type_ids.get("30")
        id_60 = appt_type_ids.get("60")

        id_30 = int(id_30) if id_30 is not None else None
        id_60 = int(id_60) if id_60 is not None else None

        minutes_30 = 0
        minutes_60 = 0

        for cert in student.certificates:
            if cert.is_expired() or cert.remaining_minutes <= 0:
                continue

            ids = set(cert.appointment_type_ids or [])

            if id_30 is not None and id_30 in ids:
                minutes_30 += cert.remaining_minutes
            if id_60 is not None and id_60 in ids:
                minutes_60 += cert.remaining_minutes

        lessons_30 = minutes_30 // 30
        lessons_60 = minutes_60 // 60

        return CommandResult(
            type_="REMAINING_LESSONS",
            content={
                "student_email": student.email,
                "instrument": instrument,
                "lessons_30": lessons_30,
                "lessons_60": lessons_60,
            },
            errors=None,
            routing=routing,
            source=source
        )
