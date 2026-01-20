class Student:

    def __init__(self, id_, first_name, surname, email):
        self.id_ = id_
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
        return [lesson for lesson in self.lessons if lesson.is_unpaid()]

    def valid_certificates_for(self, lesson):
        return [certificate for certificate in self.certificates if certificate.can_apply_to(lesson)]
