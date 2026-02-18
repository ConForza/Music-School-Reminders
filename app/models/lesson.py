from datetime import datetime

class Lesson:

    def __init__(self, id_, date_raw, type_, category, duration, payment, appointment_type_id = None, certificate_code: str = None):
        self.id_ = id_

        if date_raw.endswith("+0000"):
            date_raw = date_raw[:-5] + "+00:00"

        self.datetime = datetime.fromisoformat(date_raw)

        self.type_ = type_
        self.category = category
        self.duration = int(duration)
        self.payment = payment
        self.appointment_type_id = int(appointment_type_id) if appointment_type_id is not None else None
        self.certificate_code = certificate_code

    @property
    def date(self):
        return self.datetime.strftime("%d %b %Y")

    @property
    def time(self):
        return self.datetime.strftime("%H:%M")

    def is_paid(self):
        return self.payment.is_paid()

    def is_unpaid(self):
        return self.payment.is_unpaid()

    def is_taster(self):
        return (self.certificate_code or "").strip().upper() == "TASTER"
