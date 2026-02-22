from app.models.command_result import CommandResult
from app.services.acuity_service import fetch_appointments_for_calendar, fetch_students_for_staff, delete_appointment
from app.persistence.sqlite.staff_repository import StaffRepository
from app.persistence.sqlite.instrument_repository import InstrumentRepository

class AppointmentService:

    def __init__(self):
        self.staff_repository = StaffRepository()
        self.instrument_repository = InstrumentRepository()

    def delete_all_lessons(self, staff_id: int, date_from, date_to, routing, source, preview: bool = False):
        errors = []
        lessons_deleted = 0
        calendar_id = self.staff_repository.get_staff_calendar_id(staff_id)
        success, data_or_error = fetch_appointments_for_calendar(calendar_id, date_from, date_to)

        if not success:
            error = data_or_error
            return CommandResult(
                type_="DELETE_ALL_LESSONS",
                content={
                    "date_from": date_from,
                    "date_to": date_to,
                    "staff_id": staff_id,
                    "preview": preview
                },
                errors=[error],
                routing=routing,
                source=source
            )

        results = data_or_error
        for result in results:
            success, error = delete_appointment(result["id"], preview)
            if not success:
                errors.append(f"Failed to delete appointment id {result['id']}: {error}")
            else:
                lessons_deleted += 1

        return CommandResult(
            type_="DELETE_ALL_LESSONS",
            content={
                "date_from": date_from,
                "date_to": date_to,
                "staff_id": staff_id,
                "lessons_deleted": lessons_deleted,
                "preview": preview
            },
            errors=errors,
            routing=routing,
            source=source
        )

    def delete_student_lessons(
            self, staff_id: int, student_email: str, date_from, date_to, instrument, routing, source, preview: bool = False
    ):
        errors = []
        ids_to_delete = []
        lessons_deleted = 0
        instrument_codes = None
        staff = self.staff_repository.get_staff_record(staff_id)
        if instrument:
            instrument_codes = [code for code in self.instrument_repository.get_in_person_appointment_type_ids(instrument).values()]
        try:
            students = fetch_students_for_staff(staff, date_from, date_to)
            for student in students:
                if not student_email == student.email:
                    continue
                for lesson in student.lessons:
                    if instrument_codes is not None:
                        if lesson.appointment_type_id in instrument_codes:
                            ids_to_delete.append(lesson.id_)
                    else:
                        ids_to_delete.append(lesson.id_)

            for lesson_id in ids_to_delete:
                success, error = delete_appointment(lesson_id, preview)
                if not success:
                    errors.append(f"Failed to delete appointment id {lesson_id}: {error}")
                else:
                    lessons_deleted += 1

        except Exception as e:
            errors.append(f"{staff.name}: {str(e)}")


        return CommandResult(
            type_="DELETE_STUDENT_LESSONS",
            content={
                "student_email": student_email,
                "date_from": date_from,
                "date_to": date_to,
                "staff_id": staff_id,
                "instrument": instrument,
                "lessons_deleted": lessons_deleted,
                "preview": preview
            },
            errors=errors,
            routing=routing,
            source=source
        )