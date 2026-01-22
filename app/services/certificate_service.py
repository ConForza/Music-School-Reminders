import app.services.acuity_service as acuity_service

class CertificateService:

    def select_certificate_for_lesson(self, student, lesson):

        valid_certificates = student.valid_certificates_for(lesson)

        if not valid_certificates:
            return None

        valid_certificates.sort(key=lambda c: c.expiration_date)

        return valid_certificates[0]

    def apply_certificates_for_student(self, student):

        results = []

        for lesson in student.unpaid_lessons():
            certificate = self.select_certificate_for_lesson(student, lesson)
            if certificate is None:
                print("No valid certificate for lesson", lesson.id_)
                break
            success = acuity_service.apply_certificate_to_lesson(certificate.order_id, lesson.id_)
            if success:
                print(f"Applied certificate {certificate.order_id} to {lesson.id_}")
                results.append((lesson.id_, certificate.order_id))
                continue
            else:
                print("Failed to apply certificate to lesson", lesson.id_)
                break

        return results

