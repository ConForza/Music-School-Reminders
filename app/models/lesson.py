class Lesson:

    def __init__(self, id_, date, type_, category, duration, payment):
        self.id_ = id_
        self.date = date
        self.type_ = type_
        self.category = category
        self.duration = duration
        self.payment = payment

    def is_paid(self):
        return self.payment.is_paid == "yes"

    def apply_certificate(self, certificate):
        if certificate.apply_to_lesson(self):
            self.payment.is_paid = "yes"
            return True
        return False

