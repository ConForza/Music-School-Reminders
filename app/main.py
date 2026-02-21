from app.persistence.sqlite.staff_repository import StaffRepository

staff_repository = StaffRepository()
print(staff_repository.get_staff_calendar_id(1))