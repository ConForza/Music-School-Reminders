from app.services.acuity_service import *
from app.services.certificate_service import CertificateService
from services.report_service import ReportService
from reports.staff_daily_report import StaffDailyReport

certificate_service = CertificateService()

class DailyRunnerService:

    def __init__(self):
        self.certificate_service = CertificateService()
        self.report_service = ReportService()

    def run_daily(self, staff_members):
        for staff in staff_members:
            staff_report = StaffDailyReport(staff)
            students = fetch_students_for_staff(staff)
            for student in students:
                fetch_certificates_for_student(student)
                results = self.certificate_service.apply_certificates_for_student(student)
                for result in results:
                    staff_report.add_result(student, result)

            self.report_service.print_staff_report(staff_report)


