from app.models.command_result import CommandResult

class AppointmentService:

    def delete_all_lessons(self, staff_id: str, date_from, date_to, source, preview: bool = False):
        routing = {
            "target": "staff"
        }

        return CommandResult(
            type_="DELETE_ALL_LESSONS",
            content={
                "date_from": date_from,
                "date_to": date_to,
                "staff_id": staff_id,
                "preview": preview
            },
            errors=None,
            routing=routing,
            source=source
        )

    def delete_student_lessons(self, staff_id: str, student_email: str, date_from, date_to, source, preview: bool = False):
        routing = {
            "target": "staff"
        }

        return CommandResult(
            type_="DELETE_STUDENT_LESSONS",
            content={
                "student_email": student_email,
                "date_from": date_from,
                "date_to": date_to,
                "staff_id": staff_id,
                "preview": preview
            },
            errors=None,
            routing=routing,
            source=source
        )