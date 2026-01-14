class Certificate:

    def __init__(self, order_id, student, certificate_name, expiration_date, remaining_minutes):
        self.order_id = order_id
        self.student = student
        self.certificate_name = certificate_name
        self.expiration_date = expiration_date
        self.remaining_minutes = remaining_minutes
