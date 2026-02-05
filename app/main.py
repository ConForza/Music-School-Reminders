# app/main.py

from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.services.discord_service import DiscordService
from app.models.command_request import CommandRequest


def run_test(title: str, command_request: CommandRequest,
             command_service: CommandService,
             renderer: CommandRenderer,
             discord_service: DiscordService):
    print(f"\n=========== {title} ===========\n")

    # 1) Execute the command
    result = command_service.receive_command(command_request)
    print(f"CommandResult.type_: {result.type_}")
    print(f"CommandResult.errors: {result.errors}\n")

    # 2) Render into messages
    response = renderer.render(result)

    # 3) “Send” via DiscordService (prints to console)
    discord_service.receive_response(response)


if __name__ == "__main__":
    command_service = CommandService()
    renderer = CommandRenderer()
    discord_service = DiscordService()

    # Common routing contexts
    admin_routing = {
        "channel": "admin-channel-id",
        "guild": "guild-id-123",
        "permissions": ["Administrator"],
    }

    staff_routing = {
        "channel": "staff-channel-id",
        "guild": "guild-id-123",
        "permissions": [],  # no Administrator flag
    }

    # 1) RUN ALL STAFF (PREVIEW, ADMIN)
    req_run_all = CommandRequest(
        command="run_all_staff",
        source_id="discorduser_gary",
        args={"preview": True},
        routing=admin_routing,
    )
    run_test("RUN ALL STAFF (PREVIEW, ADMIN)",
             req_run_all, command_service, renderer, discord_service)

    # 2) RUN ALL STAFF (STAFF – should be blocked by access rules)
    req_run_all_denied = CommandRequest(
        command="run_all_staff",
        source_id="discorduser_regular_staff",
        args={"preview": True},
        routing=staff_routing,
    )
    run_test("RUN ALL STAFF (DENIED – STAFF USER)",
             req_run_all_denied, command_service, renderer, discord_service)

    # 3) REMAINING LESSONS (STAFF)
    req_remaining = CommandRequest(
        command="remaining_lessons",
        source_id="discorduser_gary",
        args={"student_email": "student@example.com"},
        routing=staff_routing,
    )
    run_test("REMAINING LESSONS",
             req_remaining, command_service, renderer, discord_service)

    # 4) GENERATE INVOICE (PREVIEW, STAFF – self only)
    req_invoice = CommandRequest(
        command="generate_invoice",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        routing=staff_routing,
    )
    run_test("GENERATE INVOICE (PREVIEW)",
             req_invoice, command_service, renderer, discord_service)

    # 5) CREATE BLOCK (PREVIEW)
    req_block = CommandRequest(
        command="create_block",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            "student_email": "student@example.com",
            "lesson_duration": 30,
            "quantity": 2,
            "preview": True,
        },
        routing=staff_routing,
    )
    run_test("CREATE BLOCK (PREVIEW)",
             req_block, command_service, renderer, discord_service)

    # 6) DELETE ALL LESSONS (PREVIEW)
    req_delete_all = CommandRequest(
        command="delete_all_lessons",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        routing=staff_routing,
    )
    run_test("DELETE ALL LESSONS (PREVIEW)",
             req_delete_all, command_service, renderer, discord_service)

    # 7) DELETE STUDENT LESSONS (PREVIEW)
    req_delete_student = CommandRequest(
        command="delete_student_lessons",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            "student_email": "student@example.com",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        routing=staff_routing,
    )
    run_test("DELETE STUDENT LESSONS (PREVIEW)",
             req_delete_student, command_service, renderer, discord_service)

    # 8) GENERATE INVOICE – MISSING ARG (should hit validate_args + error path)
    req_invoice_bad = CommandRequest(
        command="generate_invoice",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            # missing 'date_from'
            "date_to": "2026-01-31",
        },
        routing=staff_routing,
    )
    run_test("GENERATE INVOICE (MISSING ARGS)",
             req_invoice_bad, command_service, renderer, discord_service)

    # 9) INVALID COMMAND (should hit “Invalid command.” path)
    req_invalid = CommandRequest(
        command="fly_to_mars",
        source_id="discorduser_gary",
        args={},
        routing=staff_routing,
    )
    run_test("INVALID COMMAND",
             req_invalid, command_service, renderer, discord_service)
