from app.data.staff_details import STAFF_MEMBERS

class StaffService:

    def __init__(self):
        self.staff_members = STAFF_MEMBERS

        self._staff_by_discord_id = {
            staff.discord_id: staff for staff in self.staff_members
        }

    def get_all_staff(self):
        return self.staff_members

    def get_staff_by_discord_id(self, discord_id):
        return self._staff_by_discord_id.get(discord_id)
