import asyncio
import discord

from app.config import TEST_TOKEN, DAILY_REPORT_CHANNEL_ID
from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.models.command_request import CommandRequest


async def run_daily():
    client = discord.Client(intents=discord.Intents.default())
    service = CommandService()
    renderer = CommandRenderer()

    @client.event
    async def on_ready():
        print("Bot ready for scheduled run")

        request = CommandRequest(
            command="run_all_staff",
            source_id="system",
            args={
                "preview": False,
            },
            routing={"target": "staff"},
            principal_id=1,
        )

        result = service.receive_command(request)
        response = renderer.render(result)

        channel = client.get_channel(DAILY_REPORT_CHANNEL_ID)

        for msg in response.messages:
            await channel.send(msg["body"])

        await client.close()

    await client.start(TEST_TOKEN)

if __name__ == "__main__":
    asyncio.run(run_daily())