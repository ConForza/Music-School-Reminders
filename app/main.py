from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.services.discord_service import DiscordService
from app.models.command_request import CommandRequest


def run_test(label: str, command_request: CommandRequest):
    print(f"\n=========== {label} ===========\n")

    # 1) Dispatch the command
    result = command_service.receive_command(command_request)

    # Debug: show raw CommandResult
    print(f"CommandResult.type_: {result.type_}")
    print(f"CommandResult.errors: {result.errors}\n")

    # 2) Render into a CommandResponse
    response = renderer.render(result)

    # 3) “Send” via DiscordService (prints to console)
    discord_service.receive_response(response)


if __name__ == "__main__":
    command_service = CommandService()
    renderer = CommandRenderer()
    discord_service = DiscordService()

    # 1) run_all_staff (preview)
    req_run_all = CommandRequest(
        command="run_all_staff",
        source_id="discorduser_gary",
        args={"preview": True},
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("RUN ALL STAFF (PREVIEW)", req_run_all)

    # 2) remaining_lessons
    req_remaining = CommandRequest(
        command="remaining_lessons",
        source_id="discorduser_gary",
        args={"student_email": "student@example.com"},
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("REMAINING LESSONS", req_remaining)

    # 3) generate_invoice
    req_invoice = CommandRequest(
        command="generate_invoice",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,
        },
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("GENERATE INVOICE (PREVIEW)", req_invoice)

    # 4) create_block
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
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("CREATE BLOCK", req_block)

    # 5) delete_all_lessons
    req_delete_all = CommandRequest(
        command="delete_all_lessons",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            "date_from": "2026-01-01",
            "date_to": "2026-01-31",
            "preview": True,   # even if ignored now, good to have
        },
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("DELETE ALL LESSONS", req_delete_all)

    # 6) delete_student_lessons
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
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("DELETE STUDENT LESSONS", req_delete_student)

    # 7) Missing-args test (e.g. generate_invoice with no dates)
    req_invoice_bad = CommandRequest(
        command="generate_invoice",
        source_id="discorduser_gary",
        args={
            "staff_id": "Gary",
            # "date_from" missing
            "date_to": "2026-01-31",
        },
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("GENERATE INVOICE (MISSING ARGS)", req_invoice_bad)

    # 8) Invalid command test
    req_invalid = CommandRequest(
        command="fly_to_mars",
        source_id="discorduser_gary",
        args={},
        routing={"channel": "test-channel", "guild": "test-guild"}
    )
    run_test("INVALID COMMAND", req_invalid)
