from app.services.staff_service import StaffService
from app.services.daily_runner_service import DailyRunnerService


class CommandService:

    def __init__(self):
        self.staff_service = StaffService()
        self.runner = DailyRunnerService()

    def run_all_staff(self, preview=False):
        staff_members = self.staff_service.get_all_staff()
        return self.runner.run_daily(staff_members, preview=preview)

    def run_staff_by_discord_id(self, discord_id, preview=False):
        staff = self.staff_service.get_staff_by_discord_id(discord_id)

        if staff is None:
            return None

        return self.runner.run_daily([staff], preview=preview)