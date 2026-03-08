import discord
from discord import app_commands
from discord.ui import View, button
import asyncio
from app.config import TEST_TOKEN, INVOICE_CHANNEL_ID
from app.adapters.discord.discord_adapter import DiscordAdapter
from app.services.command_service import CommandService
from app.services.command_renderer import CommandRenderer
from app.persistence.sqlite.instrument_repository import InstrumentRepository

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
        self.instrument_repository = InstrumentRepository()

    async def setup_hook(self):
        await self.tree.sync()


bot = MusicSchoolBot()

class InvoicePreviewView(View):
    def __init__(self, invoice_text: str):
        super().__init__(timeout=300)
        self.invoice_text = invoice_text

    @button(label="Send invoice", style=discord.ButtonStyle.primary)
    async def send_invoice(self, interaction: discord.Interaction, button: discord.ui.Button):
        channel = interaction.client.get_channel(INVOICE_CHANNEL_ID)

        if channel is None:
            await interaction.response.edit_message(
                content="❌ Invoice channel not configured. Please contact an admin.",
                view=None
            )
            return

        await channel.send(self.invoice_text)

        try:
            await interaction.user.send(self.invoice_text)
        except discord.Forbidden:
            pass

        await interaction.response.edit_message(
            content="✅ Invoice sent.",
            view=None
        )

    @button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(
            content="❌ Invoice cancelled.",
            view=None
        )

def chunk_text(text: str, size: int = DISCORD_MAX):
    for i in range(0, len(text), size):
        yield text[i:i + size]


def run_pipeline_from_request(bot, request):
    result = bot.service.receive_command(request)
    return bot.renderer.render(result)


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
async def daily_report(interaction: discord.Interaction, preview: bool = False):
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
@app_commands.describe(
    student_email="Student email address",
    instrument="Student's instrument e.g. guitar, piano"
)
async def lessons_remaining(interaction: discord.Interaction, student_email: str, instrument: str):
    await interaction.response.defer(thinking=True, ephemeral=True)

    payload = {
        "command_name": "lessons_remaining",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": {
            "student_email": student_email,
            "instrument": instrument
        }
    }

    await run_and_send(interaction, payload, empty_message="No result returned.")


@bot.tree.command(name="create_block", description="Create block(s) of certificates for student")
@app_commands.describe(
    staff_id="Staff ID (integer). Defaults to your staff record",
    student_email="Student email address",
    instrument="Student's instrument e.g. guitar, piano",
    lesson_duration="(mins) 30 or 60",
    quantity="Number of blocks",
    preview="Run in preview mode (no real changes made)"
)
async def create_block(
        interaction: discord.Interaction,
        student_email: str,
        instrument: str,
        lesson_duration: int,
        quantity: int,
        staff_id: int | None = None,
        preview: bool = False
):
    if lesson_duration not in (30, 60):
        await interaction.response.send_message(
            "Lesson duration must be 30 or 60 minutes.",
            ephemeral=True
        )
        return

    if quantity <= 0:
        await interaction.response.send_message(
            "Quantity must be greater than zero.",
            ephemeral=True
        )
        return

    await interaction.response.defer(thinking=True)

    options = {
        "student_email": student_email,
        "lesson_duration": lesson_duration,
        "quantity": quantity,
        "instrument": instrument,
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

@bot.tree.command(name="delete_all_lessons", description="Delete all students over a given period for a staff member")
@app_commands.describe(
    date_from="Start date for deletion (format dd/mm/yy)",
    date_to="End date for deletion (format dd/mm/yy)",
    staff_id="Staff ID (integer). Defaults to your staff record",
    preview="Run in preview mode (no real changes made)"
)
async def delete_all_lessons(
        interaction: discord.Interaction,
        date_from: str,
        date_to: str,
        staff_id: int | None = None,
        preview: bool = False
):
    await interaction.response.defer(thinking=True)

    options = {
        "date_from": date_from,
        "date_to": date_to,
        "preview": preview,
    }
    if staff_id is not None:
        options["staff_id"] = staff_id

    payload = {
        "command_name": "delete_all_lessons",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": options,
    }

    await run_and_send(interaction, payload, empty_message="No result returned.")

@bot.tree.command(name="delete_student_lessons", description="Delete a students' lessons over a given period for a staff member")
@app_commands.describe(
    student_email="Student's email address",
    date_from="Start date for deletion (format dd/mm/yy)",
    date_to="End date for deletion (format dd/mm/yy)",
    staff_id="Staff ID (integer). Defaults to your staff record",
    instrument="Student's instrument e.g. guitar, piano",
    preview="Run in preview mode (no real changes made)"
)
async def delete_student_lessons(
        interaction: discord.Interaction,
        student_email: str,
        date_from: str,
        date_to: str,
        staff_id: int | None = None,
        instrument: str | None = None,
        preview: bool = False
):
    await interaction.response.defer(thinking=True)

    options = {
        "student_email": student_email,
        "date_from": date_from,
        "date_to": date_to,
        "preview": preview,
    }
    if staff_id is not None:
        options["staff_id"] = staff_id

    if instrument is not None:
        options["instrument"] = instrument

    payload = {
        "command_name": "delete_student_lessons",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": options,
    }

    await run_and_send(interaction, payload, empty_message="No result returned.")

@bot.tree.command(name="generate_invoice", description="Create an invoice for a staff member given the inputted dates")
@app_commands.describe(
    staff_id="Staff ID (integer). Defaults to your staff record",
    date_from="Start date for invoice period (format dd/mm/yy)",
    date_to="End date for invoice period (format dd/mm/yy)",
    preview="Run in preview mode (no real changes made)"
)
async def generate_invoice(
        interaction: discord.Interaction,
        date_from: str,
        date_to: str,
        staff_id: int | None = None,
        preview: bool = False
):
    await interaction.response.defer(thinking=True, ephemeral=True)

    options = {
        "date_from": date_from,
        "date_to": date_to,
        "preview": preview,
    }
    if staff_id is not None:
        options["staff_id"] = staff_id

    payload = {
        "command_name": "generate_invoice",
        "user_id": str(interaction.user.id),
        "channel_id": str(interaction.channel_id),
        "guild_id": str(interaction.guild_id),
        "options": options,
    }

    request = bot.adapter.to_command_request(payload)
    response = await asyncio.to_thread(run_pipeline_from_request, bot, request)

    invoice_text = ""
    for msg in (response.messages or []):
        body = (msg.get("body", "") or "").strip()
        if not body:
            continue
        invoice_text = body
        break

    if not invoice_text:
        await interaction.followup.send("No invoice details found.", ephemeral=True)
        return

    view = InvoicePreviewView(invoice_text=invoice_text)

    await interaction.followup.send(
        content=f"Here is your invoice preview\n\n{invoice_text}",
        view=view,
        ephemeral=True,
    )

@lessons_remaining.autocomplete("instrument")
async def lessons_remaining_instrument_autocomplete(
        interaction: discord.Interaction,
        current: str
):
    repo = bot.instrument_repository
    names = repo.search_instruments(current.strip(), limit = 25)

    return [
        app_commands.Choice(name=name, value=name) for name in names
    ]

@create_block.autocomplete("instrument")
async def create_block_instrument_autocomplete(
        interaction: discord.Interaction,
        current: str
):
    repo = bot.instrument_repository
    names = repo.search_instruments(current.strip(), limit=25)

    return [
        app_commands.Choice(name=name, value=name) for name in names
    ]

@delete_student_lessons.autocomplete("instrument")
async def delete_student_lessons_autocomplete(
        interaction: discord.Interaction,
        current: str
):
    repo = bot.instrument_repository
    names = repo.search_instruments(current.strip(), limit=25)

    return [
        app_commands.Choice(name=name, value=name) for name in names
    ]

@bot.tree.command(name="help_blocks", description="Show help for block commands")
async def help_blocks(interaction: discord.Interaction):
    text = (
        "**Block tools help**\n\n"
        "`/lessons_remaining student_email instrument`\n"
        "→ Shows remaining 30/60 minute lessons for that email+instrument.\n\n"
        "`/create_block student_email instrument lesson_duration quantity [staff_id] [preview]`\n"
        "→ Creates block(s) of 5 lessons as Acuity certificates.\n"
        "   • `lesson_duration`: 30 or 60\n"
        "   • `quantity`: number of blocks (each block = 5 lessons)\n"
        "   • `preview`: if true, just prints what would happen.\n"
    )

    await interaction.response.send_message(text, ephemeral=True)

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
