from app.models.command_response import CommandResponse
from services.report_service import ReportService


class CommandRenderer:

    def __init__(self):
        self.report_service = ReportService()

    def render(self, result):
        if result.type_ == "RUN_DAILY":
            return self._render_run_daily(result)

        raise ValueError(f"Unknown command type {result.type_}")

    def _render_run_daily(self, result):
        messages = []

        reports = result.content.get("reports", [])

        for report in reports:
            body = self._render_staff_report(report)

            messages.append({
                "to": self._resolve_destination(result.routing, report),
                "body": body,
                "type": "text"
            })

            if "admin" in result.routing["target"]:
                messages.append({
                    "to": "admin",
                    "body": body,
                    "type": "text"
                })

        return CommandResponse(
            messages=messages,
            routing=result.routing,
            errors=result.errors
        )

    def _render_staff_report(self, report):
        return self.report_service.print_staff_report(report)

    def _resolve_destination(self, routing, report):

        if "staff" in routing["target"]:
            return f"staff:{report.staff.discord_id}"
        else:
            raise ValueError(f'Unknown command type {routing["target"]}')
