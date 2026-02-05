from app.models.command_response import CommandResponse
from services.report_service import ReportService


class CommandRenderer:

    def __init__(self):
        self.report_service = ReportService()

    def render(self, result):
        if result.errors:
            return self._render_errors(result)

        if result.type_ == "RUN_DAILY":
            return self._render_run_daily(result)

        if result.type_ == "REMAINING_LESSONS":
            return self._render_remaining_lessons(result)

        if result.type_ == "CREATE_BLOCK":
            return self._render_create_block(result)

        if result.type_ == "GENERATE_INVOICE":
            return self._render_generate_invoice(result)

        if result.type_ == "DELETE_ALL_LESSONS":
            return self._render_delete_all_lessons(result)

        if result.type_ == "DELETE_STUDENT_LESSONS":
            return self._render_delete_student_lessons(result)

        raise ValueError(f"Unknown command type {result.type_}")

    def _render_errors(self, result):
        routing = result.routing or {"target": "staff"}

        if result.source:
            to = result.source
        else:
            to = "admin"

        body = "\n".join(result.errors)

        messages = [{
            "to": to,
            "body": body,
            "type": "text",
        }]

        return CommandResponse(
            messages=messages,
            routing=routing,
            errors=result.errors
        )

    def _render_run_daily(self, result):
        messages = []

        reports = result.content.get("reports", [])

        for report in reports:
            body = self._render_staff_report(report)

            messages.append({
                "to": self._resolve_destination(result),
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

    def _render_remaining_lessons(self, result):
        messages = []

        student_email = result.content.get("student_email")

        body = self.report_service.print_remaining_lessons(student_email)

        messages.append({
            "to": self._resolve_destination(result),
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

    def _render_create_block(self, result):
        messages = []

        staff_id = result.content.get("staff_id")
        student_email = result.content.get("student_email")
        lesson_duration = result.content.get("lesson_duration")
        quantity = result.content.get("quantity")
        preview = result.content.get("preview", False)

        body = self.report_service.print_block(staff_id, student_email, lesson_duration, quantity, preview)

        messages.append({
            "to": self._resolve_destination(result),
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

    def _render_generate_invoice(self, result):
        messages = []

        staff_id = result.content.get("staff_id")
        date_from = result.content.get("date_from")
        date_to = result.content.get("date_to")
        preview = result.content.get("preview", False)

        body = self.report_service.print_invoice(staff_id, date_from, date_to, preview)

        messages.append({
            "to": self._resolve_destination(result),
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

    def _render_delete_all_lessons(self, result):
        messages = []

        staff_id = result.content.get("staff_id")
        date_from = result.content.get("date_from")
        date_to = result.content.get("date_to")
        preview = result.content.get("preview", False)

        body = self.report_service.delete_all_lessons(staff_id, date_from, date_to, preview)

        messages.append({
            "to": self._resolve_destination(result),
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

    def _render_delete_student_lessons(self, result):
        messages = []

        staff_id = result.content.get("staff_id")
        student_email = result.content.get("student_email")
        date_from = result.content.get("date_from")
        date_to = result.content.get("date_to")
        preview = result.content.get("preview", False)

        body = self.report_service.delete_student_lessons(staff_id, student_email, date_from, date_to, preview)

        messages.append({
            "to": self._resolve_destination(result),
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

    def _resolve_destination(self, result):

        if not result.source:
            raise ValueError("No source set for result. Cannot route message.")

        return result.source
