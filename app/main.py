from app.services.command_service import CommandService
from app.services.report_service import ReportService

command_service = CommandService()
report_service = ReportService()

print("\n===== RUN ALL STAFF (PREVIEW) =====\n")
reports = command_service.run_all_staff(preview=True)

for report in reports:
    report_service.print_staff_report(report)

report = command_service.run_staff_by_discord_id("TEST_USER_1", preview=True)[0]
report_service.print_staff_report(report)