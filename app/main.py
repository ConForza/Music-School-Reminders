from app.persistence.sqlite.connection import Connection
from app.adapters.discord.discord_adapter import DiscordAdapter
from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.persistence.sqlite.audit_repository import AuditRepository


# ============================================================
# SEED TEST DATA
# ============================================================

def seed_users_and_staff():
    conn = Connection().create_connection()
    c = conn.cursor()

    # Clear existing data (DEV ONLY)
    c.execute("DELETE FROM audit_logs")
    c.execute("DELETE FROM staff")
    c.execute("DELETE FROM users")

    # --- Admin user ---
    c.execute("""
        INSERT INTO users (email, password_hash, discord_id, is_admin, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, ("admin@example.com", None, "discord_admin", 1))
    admin_user_id = c.lastrowid

    # --- Regular staff user ---
    c.execute("""
        INSERT INTO users (email, password_hash, discord_id, is_admin, created_at)
        VALUES (?, ?, ?, ?, datetime('now'))
    """, ("staff@example.com", None, "discord_staff", 0))
    staff_user_id = c.lastrowid

    # --- Staff rows ---
    c.execute("""
        INSERT INTO staff (user_id, first_name, surname, role, acuity_calendar_id)
        VALUES (?, ?, ?, ?, ?)
    """, (admin_user_id, "Gary", "Admin", "Teacher", 123))
    admin_staff_id = c.lastrowid

    c.execute("""
        INSERT INTO staff (user_id, first_name, surname, role, acuity_calendar_id)
        VALUES (?, ?, ?, ?, ?)
    """, (staff_user_id, "Test", "Staff", "Teacher", 456))
    staff_staff_id = c.lastrowid

    conn.commit()
    conn.close()

    print("\n=========== SEEDED USERS/STAFF ===========")
    print(f"Admin staff_id: {admin_staff_id} (discord_admin)")
    print(f"Staff staff_id: {staff_staff_id} (discord_staff)")

    return admin_staff_id, staff_staff_id


# ============================================================
# COMMAND SIMULATION HELPER
# ============================================================

adapter = DiscordAdapter()
service = CommandService()
renderer = CommandRenderer()
audit_repo = AuditRepository()


def simulate(payload, title):
    print(f"\n=========== {title} ===========")

    request = adapter.to_command_request(payload)
    print("principal_id:", getattr(request, "principal_id", None))

    result = service.receive_command(request)

    print("CommandResult.type_:", result.type_)
    print("CommandResult.errors:", result.errors)

    response = renderer.render(result)

    for msg in response.messages:
        print("\nTO:", msg["to"])
        print(msg["body"])


# ============================================================
# RUN TESTS
# ============================================================

if __name__ == "__main__":

    admin_staff_id, staff_staff_id = seed_users_and_staff()

    # --------------------------------------------------------
    # TEST 1 — Admin allowed admin_only
    # --------------------------------------------------------
    simulate({
        "command_name": "daily_report",
        "user_id": "discord_admin",
        "options": {"preview": True},
    }, "TEST 1 — Admin can run daily_report")

    # --------------------------------------------------------
    # TEST 2 — Staff denied admin_only
    # --------------------------------------------------------
    simulate({
        "command_name": "daily_report",
        "user_id": "discord_staff",
        "options": {"preview": True},
    }, "TEST 2 — Staff denied daily_report")

    # --------------------------------------------------------
    # TEST 3 — Staff allowed self staff_id
    # --------------------------------------------------------
    simulate({
        "command_name": "delete_lesson_range",
        "user_id": "discord_staff",
        "options": {
            "staff_id": staff_staff_id,
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True
        }
    }, "TEST 3 — Staff delete own lessons")

    # --------------------------------------------------------
    # TEST 4 — Staff denied wrong staff_id
    # --------------------------------------------------------
    simulate({
        "command_name": "delete_lesson_range",
        "user_id": "discord_staff",
        "options": {
            "staff_id": admin_staff_id,  # Not their own
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True
        }
    }, "TEST 4 — Staff delete OTHER lessons (denied)")

    # --------------------------------------------------------
    # TEST 5 — Unknown Discord user
    # --------------------------------------------------------
    simulate({
        "command_name": "delete_lesson_range",
        "user_id": "discord_unknown",
        "options": {
            "staff_id": staff_staff_id,
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True
        }
    }, "TEST 5 — Unknown user denied")

    # --------------------------------------------------------
    # AUDIT CHECK
    # --------------------------------------------------------
    print("\n=========== AUDIT LOGS ==========")

    simulate({
        "command_name": "audit_recent",
        "user_id": "discord_admin",
        "options": {
            "limit": 2
        }
    }, "TEST 6 — (Admin) Recent Audit Logs")

    simulate({
        "command_name": "audit_errors",
        "user_id": "discord_admin",
    }, "TEST 6 — (Admin) Recent Error Logs")

    simulate({
        "command_name": "audit_mine",
        "user_id": "discord_staff",
        "options": {
            "limit": 2
        }
    }, "TEST 6 — (Admin) Recent Audit Logs")