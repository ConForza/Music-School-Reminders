from datetime import datetime as dt

class Certificate:

    def __init__(self, order_id, lesson_type, expiration_date, remaining_minutes):
        self.order_id = order_id
        self.lesson_type = lesson_type
        self.expiration_date = expiration_date
        self.remaining_minutes = remaining_minutes

    def is_expired(self):
        return dt.now() > self.expiration_date

    def matches_lesson(self, lesson):
        return self.lesson_type in lesson.category

    def can_cover(self, lesson):
        return not self.is_expired() and self.matches_lesson(lesson) and self.remaining_minutes >= lesson.duration

    def apply_to_lesson(self, lesson):
        if not self.can_cover(lesson):
            return False

        self.remaining_minutes -= lesson.duration
        return True