from app.models.student import Student
from app.models.lesson import Lesson
from app.models.payment import Payment

class TestStudent:
    lesson1 = Lesson(
        id_=1,
        date_raw="2024-02-23",
        type_="Piano lessons",
        category="piano",
        duration=30,
        payment=Payment(is_paid_raw="yes"),
        appointment_type_id=5240856,
        certificate_code=None
    )

    lesson2 = Lesson(
        id_=2,
        date_raw="2026-01-09",
        type_="Piano lessons",
        category="piano",
        duration=30,
        payment=Payment(is_paid_raw="no"),
        appointment_type_id=5240856,
        certificate_code=None
    )

    lesson3 = Lesson(
        id_=3,
        date_raw="2025-03-20",
        type_="Piano lessons",
        category="piano",
        duration=30,
        payment=Payment(is_paid_raw="yes"),
        appointment_type_id=5240856,
        certificate_code=None
    )

    lesson4 = Lesson(
        id_=4,
        date_raw="2021-01-14",
        type_="Piano lessons",
        category="piano",
        duration=30,
        payment=Payment(is_paid_raw="no"),
        appointment_type_id=5240856,
        certificate_code=None
    )


    def test_student_with_paid_and_unpaid_lessons(self):
        student = Student(
            first_name="Joe",
            surname="Bloggs",
            email="joe@bloggs.com"
        )

        student.add_lesson(self.lesson1)
        student.add_lesson(self.lesson2)
        student.add_lesson(self.lesson3)
        student.add_lesson(self.lesson4)

        unpaid_ids = [lesson.id_ for lesson in student.unpaid_lessons()]

        assert unpaid_ids == [self.lesson4.id_, self.lesson2.id_]
