from datetime import datetime, timedelta

from app.models.payment import Payment
from app.models.lesson import Lesson
from app.models.student import Student
from app.models.certificate import Certificate
from app.services.certificate_service import CertificateService

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
    category="Piano 30",
    duration=60,
    payment=Payment("yes")
)

student.add_lesson(lesson1)
student.add_lesson(lesson2)

# Create certificates
cert1 = Certificate(
    order_id="cert_001",
    certificate_name="30 Minute Lesson Pack",
    expiration_date_raw="2026-01-30",
    remaining_minutes=150
)

cert2 = Certificate(
    order_id="cert_002",
    certificate_name="30 Minute Lesson Pack",
    expiration_date_raw="2026-01-22",
    remaining_minutes=150
)

cert3 = Certificate(
    order_id="cert_003",
    certificate_name="30 Minute Lesson Pack",
    expiration_date_raw="2026-01-21",
    remaining_minutes=150
)


student.add_certificate(cert1)
student.add_certificate(cert2)
student.add_certificate(cert3)


lesson = Lesson(
    id_="lesson_002",
    date=datetime.now(),
    type_="Piano",
    category="Piano 30",
    duration=30,
    payment=Payment("no")
)

service = CertificateService()

chosen = service.select_certificate_for_lesson(student, lesson)

if chosen:
    print("Chosen certificate:", chosen.order_id, "expires:", chosen.expiration_date)
else:
    print("No valid certificate found")