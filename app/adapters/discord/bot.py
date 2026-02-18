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
        yield text[i:i + size]


def run_pipeline_from_request(bot, request):
    result = bot.service.receive_command(request)
    return bot.renderer.render(result)


bot = MusicSchoolBot()


async def run_and_send(interaction: discord.Interaction, payload: dict, *, empty_message: str = "No results found."):
    request = bot.adapter.to_command_request(payload)
    response = await asyncio.to_thread(run_pipeline_from_request, bot, request)

    parts_to_send: list[str] = []

    for msg in (response.messages or []):
        body = (msg.get("body", "") or "").strip()
        if not body:
            continue
        for part in chunk_text(body):
            part = part.strip()
            if part:
                parts_to_send.append(part)

    if not parts_to_send:
        await interaction.followup.send(empty_message, ephemeral=True)
        return

    for part in parts_to_send:
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

    await run_and_send(interaction, payload, empty_message=f"No logs found (limit={limit}).")


@bot.tree.command(name="audit_recent", description="Show recent audit log entries (admin only)")
@app_commands.describe(limit="How many results (1–50). Default 5")
async def audit_recent(interaction: discord.Interaction, limit: int = 5):
    await interaction.response.defer(thinking=True, ephemeral=True)

    payload = {
        "command_name": "audit_recent",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": {
            "limit": limit
        }
    }

    await run_and_send(interaction, payload, empty_message=f"No logs found (limit={limit}).")


@bot.tree.command(name="audit_errors", description="Show recent audit errors (admin only)")
@app_commands.describe(limit="How many results (1–50). Default 5")
async def audit_errors(interaction: discord.Interaction, limit: int = 5):
    await interaction.response.defer(thinking=True, ephemeral=True)

    payload = {
        "command_name": "audit_errors",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": {
            "limit": limit
        }
    }

    await run_and_send(interaction, payload, empty_message=f"No errors found (limit={limit}).")


@bot.tree.command(name="lessons_remaining", description="Check remaining lessons for a student")
@app_commands.describe(student_email="Student email address")
async def lessons_remaining(interaction: discord.Interaction, student_email: str):
    await interaction.response.defer(thinking=True, ephemeral=True)

    payload = {
        "command_name": "lessons_remaining",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": {
            "student_email": student_email
        }
    }

    await run_and_send(interaction, payload, empty_message="No result returned.")


@bot.tree.command(name="create_block", description="Create block(s) of certificates for student")
@app_commands.describe(
    staff_id="Staff ID (integer). Defaults to your staff record",
    student_email="Student email address",
    lesson_duration="(mins) 30 or 60",
    quantity="Number of blocks",
    preview="Run in preview mode (no real changes made)"
)
async def create_block(
        interaction: discord.Interaction,
        student_email: str,
        lesson_duration: int,
        quantity: int,
        staff_id: int | None = None,
        preview: bool = False
):
    await interaction.response.defer(thinking=True)

    options = {

        "student_email": student_email,
        "lesson_duration": lesson_duration,
        "quantity": quantity,
        "preview": preview,
    }
    if staff_id is not None:
        options["staff_id"] = staff_id

    payload = {
        "command_name": "create_block",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": options,
    }

    await run_and_send(interaction, payload, empty_message="No result returned.")


@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    print("Unhandled app command error:", repr(error))

    if interaction.response.is_done():
        await interaction.followup.send(
            "An unexpected error occurred. The issue has been logged.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "An unexpected error occurred. The issue has been logged.",
            ephemeral=True
        )


bot.run(TOKEN)
