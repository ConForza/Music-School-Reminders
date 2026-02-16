import discord
from discord import app_commands
import asyncio
from app.config import TEST_TOKEN
from app.adapters.discord.discord_adapter import DiscordAdapter
from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer

TOKEN = TEST_TOKEN
DISCORD_MAX = 2000

class MusicSchoolBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

        self.adapter = DiscordAdapter()
        self.service = CommandService()
        self.renderer = CommandRenderer()

    async def setup_hook(self):
        await self.tree.sync()

def chunk_text(text: str, size: int = DISCORD_MAX):
    for i in range(0, len(text), size):
        yield text[i:i+size]

def run_pipeline_from_request(bot, request):
    result = bot.service.receive_command(request)
    return bot.renderer.render(result)

bot = MusicSchoolBot()

async def run_and_send(interaction: discord.Interaction, payload: dict):
    request = bot.adapter.to_command_request(payload)
    response = await asyncio.to_thread(run_pipeline_from_request, bot, request)

    if not response.messages:
        await interaction.followup.send("No output generated.", ephemeral=True)
        return

    for msg in response.messages:
        body = msg.get("body", "")
        if not body:
            continue
        for part in chunk_text(body):
            await interaction.followup.send(part)


@bot.tree.command(name="daily_report", description="Run daily staff report")
@app_commands.describe(preview="Run in preview mode (no real changes made)")
async def daily_report(interaction: discord.Interaction, preview: bool = True):
    await interaction.response.defer(thinking=True)

    payload = {
        "command_name": "daily_report",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": {
            "preview": preview
        }
    }

    await run_and_send(interaction, payload)

@bot.tree.command(name="audit_mine", description="Show your recent audit log entries")
@app_commands.describe(limit="How many results (1–50). Default 5")
async def audit_mine(interaction: discord.Interaction, limit: int = 5):
    await interaction.response.defer(thinking=True, ephemeral=True)

    payload = {
        "command_name": "audit_mine",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": {
            "limit": limit
        }
    }

    await run_and_send(interaction, payload)

bot.run(TOKEN)