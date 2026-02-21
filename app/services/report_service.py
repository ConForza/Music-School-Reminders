from app.persistence.sqlite.staff_repository import StaffRepository

class ReportService:

    BANNER = "**PREVIEW MODE**\n" \
                 "No changes have been made in Acuity.\n\n"

    def __init__(self):
        self.staff_repository = StaffRepository()

    def print_staff_report(self, staff_report):

        report = ""

        report += \
            f"\n**DAILY STAFF SUMMARY**\n👩‍🏫 **{staff_report.staff.name}**\n\n"

        for student_report in staff_report.students.values():

            student = student_report.student
            report += f"👤 **{student.first_name} {student.surname}**  ✉️ {student.email}\n"

            applied = student_report.applied_results()
            problems = student_report.problem_results()

            for r in applied:
                report += f"✅ Lesson {r.lesson_id} → {r.certificate_id} ({r.remaining_lessons} lesson(s) remaining)\n"

            for r in problems:
                if r.status == "no_valid_certificate":
                    report += f"❌ Lesson {r.lesson_id} → no valid certificate\n"
                elif r.status == "api_failed":
                    report += f"⚠️ Lesson {r.lesson_id} → API FAILED using {r.certificate_id}\n"

        return report

    def print_remaining_lessons(self, student_email, instrument, lessons_30, lessons_60):
        return (
            f"**Remaining lessons for {student_email} ({instrument})\n"
            f"–30 min: {lessons_30}\n"
            f"–60 min: {lessons_60}"
                )

    def print_block(self, staff_id, student_email, lesson_duration, quantity, instrument, preview):
        staff_name = self.staff_repository.get_name_by_staff_id(int(staff_id))
        header = ReportService.BANNER if preview else ""
        action = "would be" if preview else ""
        return (
            f"{header}{quantity} block(s) of 5x{lesson_duration} min lessons "
            f"for {student_email} ({instrument}) {action} created for {staff_name}."
        )

    def print_invoice(self, staff_id, date_from, date_to, preview):
        staff_name = self.staff_repository.get_name_by_staff_id(int(staff_id))
        if preview:
            message = "================ PREVIEW MODE ================\n" \
                 "Invoices not submitted.\n\n"
        else:
            message = ""
        message += f"""
        ================ INVOICE ================
        for: {staff_name} from {date_from} to {date_to}
        
        [LESSONS WILL GO HERE]
        
        [TOTAL WILL GO HERE]
        """
        return message

    def delete_all_lessons(self, staff_id, date_from, date_to, preview):
        staff_name = self.staff_repository.get_name_by_staff_id(int(staff_id))
        header = ReportService.BANNER if preview else ""
        if preview:
            action = f"Would delete all lessons"
        else:
            action = "All lessons deleted"
        return f"{header}{action} for {staff_name} from {date_from} to {date_to}."

    def delete_student_lessons(self, staff_id, student_email, date_from, date_to, preview):
        staff_name = self.staff_repository.get_name_by_staff_id(int(staff_id))
        header = ReportService.BANNER if preview else ""
        if preview:
            action = f"Would delete all {student_email} lessons"
        else:
            action = f"All {student_email} lessons deleted"
        return f"{header}{action} for {staff_name} from {date_from} to {date_to}."

    def print_audit_recent(self, results):
        message = ""

        for result in results:
            message += f"{result.id} user_id: {result.user_id} command: {result.command} status: {result.status}\n"

        return message

    def print_audit_errors(self, results):
        message = ""

        for result in results:
            message += f"{result.id} user_id: {result.user_id} command: {result.command} errors: {result.errors}\n"

        return message

    def print_audit_mine(self, results):
        message = ""

        for result in results:
            message += f"{result.id} command: {result.command} status: {result.status}\n"

        return message
