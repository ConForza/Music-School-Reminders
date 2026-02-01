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

    def print_remaining_lessons(self, student_email):
        return f"There are n lessons remaining for {student_email}."

    def print_block(self, staff_id, student_email, lesson_duration, quantity):
        return f"{quantity} block/s of 5 * {lesson_duration}min lessons for {student_email} created by {staff_id}."

    def print_invoice(self, staff_id, date_from, date_to):
        invoice = f"""
        ================ INVOICE ================
        for: {staff_id} from {date_from} to {date_to}
        
        [LESSONS WILL GO HERE]
        
        [TOTAL WILL GO HERE]
        """

        return invoice

    def delete_all_lessons(self, staff_id, date_from, date_to):
        return f"All lessons deleted for {staff_id} from {date_from} to {date_to}."

    def delete_student_lessons(self, staff_id, student_email, date_from, date_to):
        return f"{student_email} lessons deleted for {staff_id} from {date_from} to {date_to}."
