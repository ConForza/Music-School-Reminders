class LessonResult:

    def __init__(self, lesson_id, lesson_date, duration, status, certificate_id=None, remaining_minutes=None):
        self.lesson_id = lesson_id
        self.lesson_date = lesson_date
        self.duration = duration
        self.status = status
        self.certificate_id = certificate_id
        self.remaining_minutes = remaining_minutes