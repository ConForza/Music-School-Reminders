class CertificateService:

    def select_certificate_for_lesson(self, student, lesson):

        valid_certificates = student.valid_certificates_for(lesson)

        if not valid_certificates:
            return None

        valid_certificates.sort(key=lambda c: c.expiration_date)

        return valid_certificates[0]
