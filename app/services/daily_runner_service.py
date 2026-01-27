from app.services.acuity_service import *
from app.services.certificate_service import CertificateService
from services.report_service import ReportService
from reports.staff_daily_report import StaffDailyReport
from app.models.command_result import CommandResult


class DailyRunnerService:

    def __init__(self):
        self.certificate_service = CertificateService()
        self.report_service = ReportService()

    def run_daily(self, staff_members, preview=False):

        staff_reports = []
        errors = []

        for staff in staff_members:
            try:
                staff_report = StaffDailyReport(staff)
                students = fetch_students_for_staff(staff)
                for student in students:
                    fetch_certificates_for_student(student)
                    results = self.certificate_service.apply_certificates_for_student(student, preview=preview)
                    for result in results:
                        staff_report.add_result(student, result)

                if staff_report.has_results():
                    staff_reports.append(staff_report)

            except Exception as e:
                errors.append(f"{staff.name}: {str(e)}")

        routing = {
            "target": "staff_and_admin"
        }

        return CommandResult(
            type_="RUN_DAILY",
            content={
                "reports": staff_reports
            },
            errors=errors,
            routing=routing,
            source=None
        )
