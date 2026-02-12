# from app.services.command_service import CommandService
# from app.services.command_renderer import CommandRenderer
# from app.services.discord_service import DiscordService
# from adapters.discord.discord_adapter import DiscordAdapter
#
# command_service = CommandService()
# renderer = CommandRenderer()
# discord_service = DiscordService()
# discord_adapter = DiscordAdapter()
#
#
# def run_discord_sim(title: str, payload: dict):
#     print(f"\n=========== {title} ===========\n")
#
#     # 1) Pretend Discord called us
#     command_request = discord_adapter.to_command_request(payload)
#
#     # 2) Pass into the existing command pipeline
#     result = command_service.receive_command(command_request)
#
#     print(f"CommandResult.type_: {result.type_}")
#     print(f"CommandResult.errors: {result.errors}\n")
#
#     # 3) Render and "send" to Discord
#     response = renderer.render(result)
#     discord_service.receive_response(response)
#
#
# if __name__ == "__main__":
#     # Example: /daily_report as an admin user
#     payload_daily = {
#         "command_name": "daily_report",
#         "user_id": "discorduser_gary",
#         "channel_id": "channel_123",
#         "guild_id": "guild_123",
#         "options": {
#             "preview": True
#         },
#         "user_permissions": ["Administrator"],
#     }
#
#     run_discord_sim("DISCORD /daily_report (preview, admin)", payload_daily)
#
#     # Example: /lessons_remaining student@example.com
#     payload_lessons = {
#         "command_name": "lessons_remaining",
#         "user_id": "discorduser_gary",
#         "channel_id": "channel_123",
#         "guild_id": "guild_123",
#         "options": {
#         },
#         "user_permissions": [],  # staff, not admin
#     }
#
#     run_discord_sim("DISCORD /lessons_remaining", payload_lessons)
#
#     # Example: /create_block (preview)
#     payload_block = {
#         "command_name": "create_block",
#         "user_id": "discorduser_gary",
#         "channel_id": "channel_123",
#         "guild_id": "guild_123",
#         "options": {
#             "staff_id": "Gary",
#             "student_email": "student@example.com",
#             "lesson_duration": 30,
#             "quantity": 2,
#             "preview": True,
#         },
#         "user_permissions": [],  # staff user, not admin
#     }
#
#     run_discord_sim("DISCORD /create_block (preview)", payload_block)
#
#     # Example: /delete_lesson_range (preview)
#     payload_delete_range = {
#         "command_name": "delete_lesson_range",
#         "user_id": "discorduser_gary",
#         "channel_id": "channel_123",
#         "guild_id": "guild_123",
#         "options": {
#             "staff_id": "Gary",
#             "date_from": "2026-01-01",
#             "date_to": "2026-01-31",
#             "preview": True,
#         },
#         "user_permissions": [],  # staff user, allowed for own calendar
#     }
#
#     run_discord_sim("DISCORD /delete_lesson_range (preview)", payload_delete_range)
#
#     payload_delete_student_lessons = {
#         "command_name": "delete_student_lessons",
#         "user_id": "discorduser_gary",
#         "channel_id": "channel_123",
#         "options": {
#             "student_email": "joe@bloggs.com",
#             "staff_id": "Gary",
#             "date_from": "2026-01-01",
#             "date_to": "2026-01-31",
#             "preview": True,
#         },
#         "user_permissions": [],  # staff user, allowed for own calendar
#     }
#
#     run_discord_sim("DISCORD /delete_student_lesson (preview)", payload_delete_student_lessons)

# app/main.py

from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.services.discord_service import DiscordService
from app.adapters.discord.discord_adapter import DiscordAdapter

from app.persistence.sqlite.connection import Connection
import sqlite3


def seed_users_and_staff():
    """
    Seeds 2 users + 2 staff rows so DB-backed permission checks work.

    Assumptions:
    - users table has: id, email, password_hash, discord_id, is_admin, created_at
    - staff table has: id, user_id, first_name, surname, role, acuity_calendar_id
    - sqlite DB file is whatever your Connection() uses (e.g. app/audits.db)
    """
    conn = Connection().create_connection()
    c = conn.cursor()

    # Ensure tables exist (if your Connection already does this elsewhere, ok to keep)
    # If your Connection has create_tables(), call it here instead of raw SQL.
    # Connection().create_tables()

    # --- Insert users ---
    c.execute(
        """
        INSERT OR IGNORE INTO users (discord_id, is_admin, created_at)
        VALUES (?, ?, ?)
        """,
        ("discorduser_gary", 1, "2026-02-12T00:00:00"),
    )
    c.execute(
        """
        INSERT OR IGNORE INTO users (discord_id, is_admin, created_at)
        VALUES (?, ?, ?)
        """,
        ("discorduser_regular_staff", 0, "2026-02-12T00:00:00"),
    )

    # --- Insert staff linked to users ---
    # Admin staff row
    c.execute(
        """
        INSERT OR IGNORE INTO staff (user_id, first_name, surname, role, acuity_calendar_id)
        VALUES (
            (SELECT id FROM users WHERE discord_id = ?),
            ?, ?, ?, ?
        )
        """,
        ("discorduser_gary", "Gary", "O'Shea", "Admin", 123),
    )

    # Regular staff row
    c.execute(
        """
        INSERT OR IGNORE INTO staff (user_id, first_name, surname, role, acuity_calendar_id)
        VALUES (
            (SELECT id FROM users WHERE discord_id = ?),
            ?, ?, ?, ?
        )
        """,
        ("discorduser_regular_staff", "Test", "Staff", "Teacher", 456),
    )

    conn.commit()

    # Fetch staff ids so tests can use correct staff_id
    c.execute(
        """
        SELECT s.id
        FROM staff s
        JOIN users u ON u.id = s.user_id
        WHERE u.discord_id = ?
        """,
        ("discorduser_gary",),
    )
    admin_staff_id = c.fetchone()[0]

    c.execute(
        """
        SELECT s.id
        FROM staff s
        JOIN users u ON u.id = s.user_id
        WHERE u.discord_id = ?
        """,
        ("discorduser_regular_staff",),
    )
    staff_staff_id = c.fetchone()[0]

    conn.close()

    print("\n=========== SEEDED USERS/STAFF ===========")
    print(f"Admin staff_id: {admin_staff_id} (discorduser_gary)")
    print(f"Staff staff_id: {staff_staff_id} (discorduser_regular_staff)\n")

    return admin_staff_id, staff_staff_id

def run_discord_sim(title: str, payload: dict, command_service, renderer, discord_service, adapter):
    print(f"\n=========== {title} ===========\n")
    command_request = adapter.to_command_request(payload)
    result = command_service.receive_command(command_request)

    print(f"CommandResult.type_: {result.type_}")
    print(f"CommandResult.errors: {result.errors}\n")

    # Render + send (your DiscordService prints TO: ... lines)
    response = renderer.render(result)
    discord_service.receive_response(response)

if __name__ == "__main__":
    command_service = CommandService()
    renderer = CommandRenderer()
    discord_service = DiscordService()
    adapter = DiscordAdapter()

    admin_staff_id, staff_staff_id = seed_users_and_staff()

    # 1) Admin can run admin_only command (daily_report -> run_all_staff)
    payload_admin_daily = {
        "command_name": "daily_report",
        "user_id": "discorduser_gary",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {"preview": True},
        "user_permissions": ["Administrator"],  # admin
    }
    run_discord_sim(
        "TEST 1 — Admin can run /daily_report (admin_only)",
        payload_admin_daily,
        command_service,
        renderer,
        discord_service,
        adapter,
    )

    # 2) Staff cannot run admin_only
    payload_staff_daily = {
        "command_name": "daily_report",
        "user_id": "discorduser_regular_staff",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {"preview": True},
        "user_permissions": [],  # not admin
    }
    run_discord_sim(
        "TEST 2 — Staff denied /daily_report (admin_only)",
        payload_staff_daily,
        command_service,
        renderer,
        discord_service,
        adapter,
    )

    # 3) Staff CAN run staff_self_or_admin when staff_id matches their own
    payload_staff_self_delete_all = {
        "command_name": "delete_lesson_range",
        "user_id": "discorduser_regular_staff",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {
            "staff_id": str(staff_staff_id),  # MUST match their staff table id
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        "user_permissions": [],
    }
    run_discord_sim(
        "TEST 3 — Staff allowed delete_lesson_range when staff_id is self",
        payload_staff_self_delete_all,
        command_service,
        renderer,
        discord_service,
        adapter,
    )

    # 4) Staff denied when staff_id is someone else's
    payload_staff_other_delete_all = {
        "command_name": "delete_lesson_range",
        "user_id": "discorduser_regular_staff",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {
            "staff_id": str(admin_staff_id),  # trying admin's staff_id
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        "user_permissions": [],
    }
    run_discord_sim(
        "TEST 4 — Staff denied delete_lesson_range when staff_id is NOT self",
        payload_staff_other_delete_all,
        command_service,
        renderer,
        discord_service,
        adapter,
    )

    # Optional: unknown user should fail staff_self_or_admin (user not found)
    payload_unknown_user = {
        "command_name": "delete_lesson_range",
        "user_id": "discorduser_unknown",
        "channel_id": "channel_123",
        "guild_id": "guild_123",
        "options": {
            "staff_id": str(staff_staff_id),
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        "user_permissions": [],
    }
    run_discord_sim(
        "OPTIONAL — Unknown user denied (user not found)",
        payload_unknown_user,
        command_service,
        renderer,
        discord_service,
        adapter,
    )