from app.models.command_request import CommandRequest

class DiscordAdapter:

    def to_command_request(self, payload: dict) -> CommandRequest:
        command_name = payload["command_name"]

        command_map = {
            "daily_report": "run_all_staff",
            "lessons_remaining": "remaining_lessons",
            "invoice": "generate_invoice",
            "create_block": "create_block",
            "delete_lesson_range": "delete_all_lessons",
            "delete_student_lessons": "delete_student_lessons",
        }

        internal_command = command_map.get(command_name, command_name)

        options = payload.get("options", {})
        args = dict(options)

        source_id = payload["user_id"]
        routing = {
            "channel": payload.get("channel_id"),
            "guild": payload.get("guild_id"),
            "permissions": payload.get("user_permissions", [])
        }

        return CommandRequest(
            command=internal_command,
            source_id=source_id,
            args=args,
            routing=routing
        )

    def to_discord_messages(self, response):
        messages = []

        for msg in response.messages:
            messages.append({
                "target": msg["to"],
                "content": msg["body"],
            })

        return messages