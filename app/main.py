from app.models.student import Student
from app.models.lesson import Lesson
from app.models.payment import Payment
from app.models.certificate import Certificate
from app.services.certificate_service import CertificateService

# ---- Create a student ----

student = Student(
    id_=1,
    first_name="Gary",
    surname="O'Shea",
    email="gary@example.com"
)

# ---- Create lessons (some unpaid, some paid) ----

lesson1 = Lesson(
    id_=101,
    date="2026-01-22T10:00:00",
    type_="Piano",
    category="30 Minute Lesson",
    duration=30,
    payment=Payment(is_paid_raw="no")
)

lesson2 = Lesson(
    id_=102,
    date="2026-01-22T11:00:00",
    type_="Piano",
    category="1 Hour Lesson",
    duration=60,
    payment=Payment(is_paid_raw="no")
)

lesson3 = Lesson(
    id_=103,
    date="2026-01-22T12:00:00",
    type_="Piano",
    category="30 Minute Lesson",
    duration=30,
    payment=Payment(is_paid_raw="yes")   # already paid
)

student.add_lesson(lesson1)
student.add_lesson(lesson2)
student.add_lesson(lesson3)

# ---- Create certificates ----

# Valid for 30 min, expires soon
cert1 = Certificate(
    order_id="CERT-001",
    certificate_name="30 Minute Lessons",
    expiration_date_raw="2026-02-01",
    remaining_minutes=150
)

# Valid for 1 hour, expires later
cert2 = Certificate(
    order_id="CERT-002",
    certificate_name="1 Hour Lessons",
    expiration_date_raw="2026-06-01",
    remaining_minutes=300
)

# Expired certificate (should never be used)
cert3 = Certificate(
    order_id="CERT-003",
    certificate_name="30 Minute Lessons",
    expiration_date_raw="2025-12-01",
    remaining_minutes=150
)

student.add_certificate(cert1)
student.add_certificate(cert2)
student.add_certificate(cert3)

# ---- Run certificate service ----

service = CertificateService()

results = service.apply_certificates_for_student(student)

# ---- Print structured results ----

print("\nFinal results:\n")

for r in results:
    if r["status"] == "applied":
        print(f"Lesson {r['lesson_id']} → applied {r['certificate_id']} "
              f"(remaining {r['remaining_minutes']} mins)")

    elif r["status"] == "no_valid_certificate":
        print(f"Lesson {r['lesson_id']} → no valid certificate")

    elif r["status"] == "api_failed":
        print(f"Lesson {r['lesson_id']} → API FAILED using {r['certificate_id']}")