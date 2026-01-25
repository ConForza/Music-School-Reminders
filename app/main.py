from app.services.daily_runner_service import DailyRunnerService
from app.data.staff_details import STAFF_MEMBERS

runner = DailyRunnerService()
runner.run_daily(STAFF_MEMBERS)