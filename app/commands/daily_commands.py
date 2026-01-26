from app.services.daily_runner_service import DailyRunnerService
from app.services.staff_service import StaffService
from app.services.report_service import ReportService


class DailyCommands:

    def __init__(self):
        self.runner = DailyRunnerService()
        self.staff_service = StaffService()
        self.report_service = ReportService()

    def run_all_staff(self):
        staff_members = self.staff_service.get_all_staff()
        reports = self.runner.run_daily(staff_members)

        for report in reports:
            self.report_service.print_staff_report(report)


    def run_staff_by_discord_id(self, discord_id):
        staff = self.staff_service.get_staff_by_discord_id(discord_id)
        if staff is None:
            return None

        return self.runner.run_daily([staff])

    def preview_staff_by_discord_id(self, discord_id):
        staff = self.staff_service.get_staff_by_discord_id(discord_id)
        if staff is None:
            return None

        reports = self.runner.run_daily([staff], preview=True)

        for report in reports:
            self.report_service.print_staff_report(report)
