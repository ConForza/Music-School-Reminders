from datetime import datetime, timedelta

from app.models.payment import Payment
from app.models.lesson import Lesson
from app.models.student import Student
from app.models.certificate import Certificate

# Create student
student = Student(
    id_="stu_001",
    first_name="Gary",
    surname="O'Shea",
    email="gary@example.com"
)

# Create lessons
lesson1 = Lesson(
    id_="lesson_001",
    date=datetime.now(),
    type_="Piano",
    category="Piano 30",
    duration=30,
    payment=Payment("no")
)

lesson2 = Lesson(
    id_="lesson_002",
    date=datetime.now(),
    type_="Piano",
    category="Piano 60",
    duration=60,
    payment=Payment("yes")
)

student.add_lesson(lesson1)
student.add_lesson(lesson2)

# Create certificates
valid_certificate = Certificate(
    order_id="cert_001",
    certificate_name="30 Minute Lesson Pack",
    expiration_date=datetime.now() + timedelta(days=10),
    remaining_minutes=120
)

expired_certificate = Certificate(
    order_id="cert_002",
    certificate_name="30 Minute Lesson Pack",
    expiration_date=datetime.now() - timedelta(days=1),
    remaining_minutes=120
)

wrong_type_certificate = Certificate(
    order_id="cert_003",
    certificate_name="1 Hour Lesson Pack",
    expiration_date=datetime.now() + timedelta(days=10),
    remaining_minutes=120
)

student.add_certificate(valid_certificate)
student.add_certificate(expired_certificate)
student.add_certificate(wrong_type_certificate)

# Test Payment + Lesson
print("Lesson 1 paid?", lesson1.is_paid())
print("Lesson 1 unpaid?", lesson1.is_unpaid())

print("Lesson 2 paid?", lesson2.is_paid())
print("Lesson 2 unpaid?", lesson2.is_unpaid())

# Test Certificate logic
print("Valid cert can apply to lesson 1?", valid_certificate.can_apply_to(lesson1))
print("Expired cert can apply to lesson 1?", expired_certificate.can_apply_to(lesson1))
print("Wrong type cert can apply to lesson 1?", wrong_type_certificate.can_apply_to(lesson1))

# Test Student orchestration
print("\nUnpaid lessons:")
for lesson in student.unpaid_lessons():
    print("-", lesson.id_)

print("\nValid certificates for lesson 1:")
for cert in student.valid_certificates_for(lesson1):
    print("-", cert.order_id)