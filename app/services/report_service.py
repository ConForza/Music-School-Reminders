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

    def print_block(self, staff_id, student_email, lesson_duration, quantity, preview):
        header = "================ PREVIEW MODE ================\n" if preview else ""
        action = "would be" if preview else ""
        return f"{header}{quantity} block/s of 5 * {lesson_duration}min lessons for {student_email} {action} created by {staff_id}."

    def print_invoice(self, staff_id, date_from, date_to, preview):
        if preview:
            message = "================ PREVIEW MODE ================\n"
        else:
            message = ""
        message += f"""
        ================ INVOICE ================
        for: {staff_id} from {date_from} to {date_to}
        
        [LESSONS WILL GO HERE]
        
        [TOTAL WILL GO HERE]
        """
        return message

    def delete_all_lessons(self, staff_id, date_from, date_to, preview):
        header = "================ PREVIEW MODE ================\n" if preview else ""
        if preview:
            action = "Would delete all lessons"
        else:
            action = "All lessons deleted"
        return f"{header}{action} for {staff_id} from {date_from} to {date_to}."

    def delete_student_lessons(self, staff_id, student_email, date_from, date_to, preview):
        header = "================ PREVIEW MODE ================\n" if preview else ""
        if preview:
            action = f"Would delete all {student_email} lessons"
        else:
            action = f"All {student_email} lessons deleted"
        return f"{header}{action} for {staff_id} from {date_from} to {date_to}."
