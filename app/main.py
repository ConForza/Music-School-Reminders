from app.models.student import Student
from app.models.lesson import Lesson
from app.models.payment import Payment
from app.models.certificate import Certificate
from app.services.certificate_service import CertificateService
from app.services.report_service import StaffDailyReport
from app.services.report_service import ReportService
import app.services.acuity_service as acuity_service
from app.data.staff_example import STAFF_MEMBERS

report_service = ReportService()
staff = STAFF_MEMBERS[0]
# -------------------------------------------------
# API STUB (temporary – will be replaced by real API)
# -------------------------------------------------

def apply_certificate_stub(order_id, lesson_id):
    print(f"[API STUB] Applying certificate {order_id} to lesson {lesson_id}")

    # Simulate API failure for a specific lesson if desired
    if lesson_id == 301:
        return False, None

    # Simulate remaining minutes returned by API
    remaining_minutes = 120
    return True, remaining_minutes


# Monkey-patch the real function for testing
acuity_service.apply_certificate_to_lesson = apply_certificate_stub


# -------------------------------------------------
# SCENARIO 1 — NORMAL HAPPY PATH
# -------------------------------------------------

print("\n================ SCENARIO 1: HAPPY PATH ================\n")

student = Student(
    id_=1,
    first_name="Joe",
    surname="Bloggs",
    email="jo@example.com"
)

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

cert1 = Certificate(
    order_id="CERT-001",
    certificate_name="30 Minute Lessons",
    expiration_date_raw="2026-02-01",
    remaining_minutes=150
)

cert2 = Certificate(
    order_id="CERT-002",
    certificate_name="1 Hour Lessons",
    expiration_date_raw="2026-06-01",
    remaining_minutes=300
)

cert3 = Certificate(
    order_id="CERT-003",
    certificate_name="30 Minute Lessons",
    expiration_date_raw="2025-12-01",   # expired
    remaining_minutes=150
)

student.add_certificate(cert1)
student.add_certificate(cert2)
student.add_certificate(cert3)

service = CertificateService()
results = service.apply_certificates_for_student(student)

report = StaffDailyReport(staff)

for r in results:
    report.add_result(student, r)

report_service.print_staff_report(report)


# -------------------------------------------------
# SCENARIO 2 — NO VALID CERTIFICATE
# -------------------------------------------------

print("\n\n================ SCENARIO 2: NO VALID CERTIFICATE ================\n")

student2 = Student(
    id_=2,
    first_name="Late",
    surname="Payer",
    email="late@example.com"
)

lesson_a = Lesson(
    id_=201,
    date="2026-01-22T09:00:00",
    type_="Guitar",
    category="30 Minute Lesson",
    duration=30,
    payment=Payment(is_paid_raw="no")
)

# Only 60-minute certificate, lesson is 30 → no match
wrong_cert = Certificate(
    order_id="CERT-010",
    certificate_name="1 Hour Lessons",
    expiration_date_raw="2026-06-01",
    remaining_minutes=300
)

student2.add_lesson(lesson_a)
student2.add_certificate(wrong_cert)

results = service.apply_certificates_for_student(student2)

report2 = StaffDailyReport(staff)

for r in results:
    report2.add_result(student2, r)

report_service.print_staff_report(report2)


# -------------------------------------------------
# SCENARIO 3 — API FAILURE
# -------------------------------------------------

print("\n\n================ SCENARIO 3: API FAILURE ================\n")

student3 = Student(
    id_=3,
    first_name="API",
    surname="Failure",
    email="api@example.com"
)

lesson_x = Lesson(
    id_=301,   # this one will fail in stub
    date="2026-01-22T10:00:00",
    type_="Piano",
    category="30 Minute Lesson",
    duration=30,
    payment=Payment(is_paid_raw="no")
)

lesson_y = Lesson(
    id_=302,
    date="2026-01-22T11:00:00",
    type_="Piano",
    category="30 Minute Lesson",
    duration=30,
    payment=Payment(is_paid_raw="no")
)

student3.add_lesson(lesson_x)
student3.add_lesson(lesson_y)

cert_ok = Certificate(
    order_id="CERT-020",
    certificate_name="30 Minute Lessons",
    expiration_date_raw="2026-03-01",
    remaining_minutes=150
)

student3.add_certificate(cert_ok)

results = service.apply_certificates_for_student(student3)

report3 = StaffDailyReport(staff)

for r in results:
    report3.add_result(student3, r)


report_service.print_staff_report(report3)