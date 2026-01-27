class ReportService:

    def print_staff_report(self, staff_report):

        report = ""

        report += \
            f"\n================ DAILY STAFF SUMMARY ================\nStaff: {staff_report.staff.name}\n\n"

        for student_report in staff_report.students.values():

            student = student_report.student
            report += f"Student: {student.first_name} {student.surname} ({student.email})\n"

            applied = student_report.applied_results()
            problems = student_report.problem_results()

            for r in applied:
                report += f"  ✔ Lesson {r.lesson_id} → {r.certificate_id} (remaining {r.remaining_minutes} mins)\n"

            for r in problems:
                if r.status == "no_valid_certificate":
                    report += f"  ✖ Lesson {r.lesson_id} → no valid certificate\n"
                elif r.status == "api_failed":
                    report += f"  ⚠ Lesson {r.lesson_id} → API FAILED using {r.certificate_id}\n"

        return report