from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.services.discord_service import DiscordService
from adapters.discord.discord_adapter import DiscordAdapter

command_service = CommandService()
renderer = CommandRenderer()
discord_service = DiscordService()
discord_adapter = DiscordAdapter()


def run_discord_sim(title: str, payload: dict):
    print(f"\n=========== {title} ===========\n")

    # 1) Pretend Discord called us
    command_request = discord_adapter.to_command_request(payload)

    # 2) Pass into the existing command pipeline
    result = command_service.receive_command(command_request)

    print(f"CommandResult.type_: {result.type_}")
    print(f"CommandResult.errors: {result.errors}\n")

    # 3) Render and "send" to Discord
    response = renderer.render(result)
    discord_service.receive_response(response)


if __name__ == "__main__":
    # Example: /daily_report as an admin user
    payload_daily = {
        "command_name": "daily_report",
        "user_id": "discorduser_gary",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {
            "preview": True
        },
        "user_permissions": ["Administrator"],
    }

    run_discord_sim("DISCORD /daily_report (preview, admin)", payload_daily)

    # Example: /lessons_remaining student@example.com
    payload_lessons = {
        "command_name": "lessons_remaining",
        "user_id": "discorduser_gary",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {
        },
        "user_permissions": [],  # staff, not admin
    }

    run_discord_sim("DISCORD /lessons_remaining", payload_lessons)

    # Example: /create_block (preview)
    payload_block = {
        "command_name": "create_block",
        "user_id": "discorduser_gary",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {
            "staff_id": "Gary",
            "student_email": "student@example.com",
            "lesson_duration": 30,
            "quantity": 2,
            "preview": True,
        },
        "user_permissions": [],  # staff user, not admin
    }

    run_discord_sim("DISCORD /create_block (preview)", payload_block)

    # Example: /delete_lesson_range (preview)
    payload_delete_range = {
        "command_name": "delete_lesson_range",
        "user_id": "discorduser_gary",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {
            "staff_id": "Gary",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        "user_permissions": [],  # staff user, allowed for own calendar
    }

    run_discord_sim("DISCORD /delete_lesson_range (preview)", payload_delete_range)

    payload_delete_student_lessons = {
        "command_name": "delete_student_lessons",
        "user_id": "discorduser_gary",
        "channel_id": "channel_123",
        "options": {
            "student_email": "joe@bloggs.com",
            "staff_id": "Gary",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        "user_permissions": [],  # staff user, allowed for own calendar
    }

    run_discord_sim("DISCORD /delete_student_lesson (preview)", payload_delete_student_lessons)
from persistence.sqlite.audit_repository import AuditRepository
from services.audit_logger import AuditLogger

# import sqlite3
#
# conn = sqlite3.connect("audits.db")
# c = conn.cursor()
#
# c.execute("SELECT id, timestamp, command, source_id, status FROM audit_logs")
# rows = c.fetchall()
#
# for row in rows:
#     print(row)
#
# conn.close()

# from services.audit_logger import AuditLogger
#
# from app.services.audit_logger import AuditLogger
#
#
print("\n=========== RECENT AUDIT ERRORS ===========\n")
audit_logger = AuditLogger()
for exec in audit_logger.recent_errors(5):
    print(f"[{exec.id}] {exec.timestamp} :: {exec.command} ({exec.status})")
    print(f"  source={exec.source_id}")
    print(f"  args={exec.args}")
    if exec.errors:
        print(f"  errors={exec.errors}")
    print()

audit_repository = AuditRepository()
for exec in audit_repository.get_recent(5):
    print(exec.id, exec.user_id, exec.command, exec.status)

# from app.persistence.sqlite.audit_repository import AuditRepository
#
# repo = AuditRepository()
# for exec in repo.get_recent_for_user(user_id=1, limit=5):
#     print(exec.id, exec.command, exec.status)