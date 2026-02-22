from app.persistence.sqlite.staff_repository import StaffRepository

class ReportService:

    BANNER = "**PREVIEW MODE**\n" \
                 "No changes have been made in Acuity.\n\n"

    def __init__(self):
        self.staff_repository = StaffRepository()

    def print_staff_report(self, staff_report, preview):

        report = ""
        if preview:
            report += ReportService.BANNER

        report += \
            f"**DAILY STAFF SUMMARY**\n👩‍🏫 **{staff_report.staff.name}**\n\n"

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
            f"**Remaining lessons for {student_email} ({instrument.lower()})\n"
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

    def print_invoice(self, staff_id, date_from, date_to, lessons, total_amount, preview):
        staff_name = self.staff_repository.get_name_by_staff_id(int(staff_id))
        max_name_width = 14

        if lessons:
            longest_name = max(len(l["name"]) for l in lessons)
        else:
            longest_name = len("Name")

        name_width = min(max(longest_name, len("Name")), max_name_width)

        def shorten(name: str) -> str:
            if len(name) <= name_width:
                return name
            return name[: name_width - 1] + "…"

        message = ""

        if preview:
            message += ReportService.BANNER

        message += f"**INVOICE**\nfor: {staff_name} from {date_from} to {date_to}\n\n"

        message += "```\n"

        message += (
            f"{'Pd':<2} "
            f"{'Name':<{name_width}}  "
            f"{'Dur':>3}  "
            f"{'Amt':>7}\n"
        )

        line_len = 2 + 1 + name_width + 2 + 3 + 2 + 8
        message += "-" * line_len + "\n"

        for lesson in lessons:
            paid_icon = "✅" if lesson["lesson_paid"] else "❌"
            name = shorten(lesson["name"])

            message += (
                f"{paid_icon:<1} "
                f"{name:<{name_width}}  "
                f"{lesson['duration']:>3}  "
                f"£{lesson['lesson_cut']:>6.2f}\n"
            )

        message += "-" * line_len + "\n"
        message += (
            f"{'':<2} "
            f"{'TOTAL':<{name_width}}  "
            f"{'':>3}  "
            f"£{total_amount:>6.2f}\n"
        )

        message += "```"
        return message

    def delete_all_lessons(self, staff_id, date_from, date_to, lessons_deleted, errors, preview):
        problems = ""
        staff_name = self.staff_repository.get_name_by_staff_id(int(staff_id))
        header = ReportService.BANNER if preview else ""
        if preview:
            action = f"Would delete all lessons"
        else:
            action = "All lessons deleted"
            if errors:
                problems = f"Total errors: {len(errors)}\n"
                for error in errors:
                    problems += f"– {error}\n"
        return (
            f"{header}{action} for {staff_name} from {date_from} to {date_to}. Total number of lessons: {lessons_deleted}.\n\n"
            f"{problems}"
                )

    def delete_student_lessons(self, staff_id, student_email, date_from, date_to, instrument, lessons_deleted, errors, preview):
        problems = ""
        staff_name = self.staff_repository.get_name_by_staff_id(int(staff_id))
        header = ReportService.BANNER if preview else ""
        lesson_type = instrument if instrument else ""
        if preview:
            action = f"Would delete all {lesson_type.lower()} lessons for {student_email}"
        else:
            action = f"All {lesson_type.lower()} lessons deleted for {student_email}"
        if errors:
            problems = f"Total errors: {len(errors)}\n"
            for error in errors:
                problems += f"– {error}\n"
        return (
            f"{header}{action} for {staff_name} from {date_from} to {date_to}. Total number of lessons: {lessons_deleted}.\n\n"
            f"{problems}"
        )

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
