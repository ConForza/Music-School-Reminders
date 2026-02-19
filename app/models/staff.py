class Staff:

    def __init__(
            self,
            id_,
            user_id,
            first_name,
            surname,
            role,
            acuity_calendar_id,
            discord_id=None
    ):
        self.id_ = int(id_)
        self.user_id = int(user_id) if user_id is not None else None
        self.first_name = first_name or ""
        self.surname = surname or ""
        self.role = role
        self.acuity_calendar_id = int(acuity_calendar_id) if acuity_calendar_id is not None else None
        self.discord_id = discord_id

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.surname}".strip()

    @property
    def calendar_id(self) -> int | None:
        return self.acuity_calendar_id
