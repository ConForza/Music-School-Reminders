from datetime import datetime, date

class Certificate:

    def __init__(self, order_id, certificate_name, expiration_date_raw, remaining_minutes):
        self.order_id = order_id
        self.certificate_name = certificate_name
        self.expiration_date = datetime.strptime(expiration_date_raw, "%Y-%m-%d").date()
        self.remaining_minutes = int(remaining_minutes)

    def is_expired(self):
        return date.today() > self.expiration_date

    def matches_lesson(self, lesson):
        if lesson.duration == 30 and "30" in self.certificate_name:
            return True

        if lesson.duration == 60 and "1 Hour" in self.certificate_name:
            return True

        return False

    def has_enough_minutes(self, lesson):
        return self.remaining_minutes >= lesson.duration

    def can_apply_to(self, lesson):
        if self.is_expired():
            return False

        if not self.matches_lesson(lesson):
            return False

        if not self.has_enough_minutes(lesson):
            return False

        return True