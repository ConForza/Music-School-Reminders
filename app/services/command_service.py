from app.services.staff_service import StaffService
from app.services.daily_runner_service import DailyRunnerService
from app.models.command_result import CommandResult


class CommandService:

    def __init__(self):
        self.staff_service = StaffService()
        self.runner = DailyRunnerService()

    def receive_command(self, command_request):
        if command_request.command == "run_all_staff":
            return self.run_all_staff(preview=command_request.args["preview"])

    def run_all_staff(self, preview=False):
        staff_members = self.staff_service.get_all_staff()
        return self.runner.run_daily(staff_members, preview=preview)

    def run_staff_by_discord_id(self, discord_id, preview=False):
        staff = self.staff_service.get_staff_by_discord_id(discord_id)

        if staff is None:
            return CommandResult(
                type_="RUN_STAFF",
                content={},
                errors=[f"No staff found for discord id {discord_id}"],
                routing={"target": "admin"},
                source=discord_id
            )

        return self.runner.run_daily([staff], preview=preview)
