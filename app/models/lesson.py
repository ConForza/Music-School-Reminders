class Lesson:

    def __init__(self, id_, date, type_, category, duration, payment):
        self.id_ = id_
        self.date = date
        self.type_ = type_
        self.category = category
        self.duration = duration
        self.payment = payment

    def is_unpaid(self):
        return not self.payment.is_paid

