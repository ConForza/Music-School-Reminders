from app.reports.staff_daily_report import StaffDailyReport

class ReportService:

    def print_staff_report(self, staff_report):

        print("\n================ DAILY STAFF SUMMARY ================\n")
        print(f"Staff: {staff_report.staff.name}\n")

        for student_report in staff_report.students.values():

            student = student_report.student
            print(f"Student: {student.first_name} {student.surname} ({student.email})")

            applied = student_report.applied_results()
            problems = student_report.problem_results()

            for r in applied:
                print(f"  ✔ Lesson {r.lesson_id} → {r.certificate_id} "
                      f"(remaining {r.remaining_minutes} mins)")

            for r in problems:
                if r.status == "no_valid_certificate":
                    print(f"  ✖ Lesson {r.lesson_id} → no valid certificate")
                elif r.status == "api_failed":
                    print(f"  ⚠ Lesson {r.lesson_id} → API FAILED using {r.certificate_id}")

            print()