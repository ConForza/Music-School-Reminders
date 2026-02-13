from app.models.command_request import CommandRequest
from persistence.sqlite.user_repository import UserRepository

class DiscordAdapter:

    def __init__(self):
        self.user_repository = UserRepository()

    def to_command_request(self, payload: dict) -> CommandRequest:
        command_name = payload["command_name"]

        command_map = {
            "daily_report": "run_all_staff",
            "lessons_remaining": "remaining_lessons",
            "invoice": "generate_invoice",
            "create_block": "create_block",
            "delete_lesson_range": "delete_all_lessons",
            "delete_student_lessons": "delete_student_lessons",
            "audit_recent": "audit_recent",
            "audit_errors": "audit_errors",
            "audit_mine": "audit_mine"
        }

        internal_command = command_map.get(command_name, command_name)

        options = payload.get("options", {})
        args = dict(options)

        source_id = payload.get("user_id")

        principal_id = self.user_repository.find_id_by_discord_id(source_id)

        routing = {
            "channel": payload.get("channel_id"),
            "guild": payload.get("guild_id"),
        }

        return CommandRequest(
            command=internal_command,
            source_id=source_id,
            args=args,
            routing=routing,
            principal_id=principal_id
        )

    def to_discord_messages(self, response):
        messages = []

        for msg in response.messages:
            messages.append({
                "target": msg["to"],
                "content": msg["body"],
            })

        return messages