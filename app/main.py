from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.services.discord_service import DiscordService
from app.models.command_request import CommandRequest

command_service = CommandService()
renderer = CommandRenderer()
discord_service = DiscordService()

command_request = CommandRequest(
    command="remaining_lessons",
    source_id="discorduser123",
    args={"preview": True, "student_email": "joe@bloggs.com"},
    routing={"channel": "4325643564", "guild": "246356745674567", "permissions": ["Administrator"]}
)

result = command_service.receive_command(command_request)
response = renderer.render(result)
discord_service.receive_response(response)
