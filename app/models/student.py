class Student:

    def __init__(self, first_name, surname, email):
        self.first_name = first_name
        self.surname = surname
        self.email = email
        self.lessons = []
        self.certificates = []

    def add_lesson(self, lesson):
        self.lessons.append(lesson)

    def add_certificate(self, certificate):
        self.certificates.append(certificate)

    def unpaid_lessons(self):
        unpaid = [lesson for lesson in self.lessons if lesson.is_unpaid()]
        return sorted(unpaid, key=lambda l: l.datetime)

    def valid_certificates_for(self, lesson):
        return [certificate for certificate in self.certificates if certificate.can_apply_to(lesson)]
