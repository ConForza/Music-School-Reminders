from app.data.staff_details import STAFF_MEMBERS
from app.services.acuity_service import fetch_students_for_staff

for staff in STAFF_MEMBERS:
    students = fetch_students_for_staff(staff)

    for student in students:
        print(student.email, len(student.lessons), len(student.unpaid_lessons()))