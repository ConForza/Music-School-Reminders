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

    def apply_certificates_for_student(self, student, preview=False):

        results = []

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

            success, remaining_minutes = acuity_service.apply_certificate_to_lesson(
                certificate.order_id,
                lesson.id_,
                preview=preview
            )

            if success:
                results.append(LessonResult(
                    lesson_id=lesson.id_,
                    lesson_date=lesson.date,
                    duration=lesson.duration,
                    status="applied",
                    certificate_id=certificate.order_id,
                    remaining_minutes=remaining_minutes
                ))
                continue
            else:
                results.append(LessonResult(
                    lesson_id=lesson.id_,
                    lesson_date=lesson.date,
                    duration=lesson.duration,
                    status="api_failed",
                    certificate_id=certificate.order_id,
                ))
                continue

        return results

    def create_block(self, staff_id: str, student_email: str, lesson_duration: int, quantity: int, source, preview: bool = False):
        routing = {
            "target": "staff"
        }

        return CommandResult(
            type_="CREATE_BLOCK",
            content={
                "student_email": student_email,
                "staff_id": staff_id,
                "lesson_duration": lesson_duration,
                "quantity": quantity,
                "preview": preview
            },
            errors=None,
            routing=routing,
            source=source
        )

    def remaining_lessons(self, student_email: str, source):

        routing = {
            "target": "staff"
        }

        return CommandResult(
            type_="REMAINING_LESSONS",
            content={
                "student_email": student_email
            },
            errors=None,
            routing=routing,
            source=source
        )
