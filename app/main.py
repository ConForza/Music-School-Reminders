from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.services.discord_service import DiscordService
from app.models.command_request import CommandRequest

command_service = CommandService()
renderer = CommandRenderer()
discord_service = DiscordService()

command_request = CommandRequest(
    command="delete_student_lessons",
    source_id="discorduser123",
    args={"preview": True, "staff_id": "John", "student_email": "joe@bloggs.com", "date_from": "01-01-26", "date_to": "01-02-26"},
    routing={"channel": "4325643564", "guild": "246356745674567", "permissions": ["Administrator"]}
)

result = command_service.receive_command(command_request)
response = renderer.render(result)
discord_service.receive_response(response)
