class Payment:

    def __init__(self, is_paid_raw):
        self.is_paid_raw = is_paid_raw

    def is_paid(self):
        return self.is_paid_raw == "yes"

    def is_unpaid(self):
        return not self.is_paid()
