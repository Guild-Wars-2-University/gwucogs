import datetime
import discord
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.commands import Cog


class TimeStamps(Cog):
    """Retrieve timestamps relative to current time."""

    __author__ = "noahdm4321"
    __version__ = "1.0"

    def __init__(self, bot: Red):
        self.bot = bot

    def format_help_for_context(self, ctx: commands.Context) -> str:
        context = super().format_help_for_context(ctx)
        return f"{context}\n\nAuthor: {self.__author__}\nVersion: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):
        return

    @app_commands.command(name="timestamp", description="Create a discord timestamp relative to the current time")
    async def timestamp(self, interaction: discord.Interaction, weeks: int=0, days: int=0, hours: int=0, minutes: int=0):
        ts = datetime.datetime.now() + datetime.timedelta(minutes=minutes) + datetime.timedelta(hours=hours) + datetime.timedelta(days=days) + datetime.timedelta(weeks=weeks)
        ts = int(ts.timestamp())

        message = ""
        for i in "fdt":
            message += f"`<t:{ts}:{i.upper()}>`: <t:{ts}:{i.upper()}>\n"
            message += f"`<t:{ts}:{i.lower()}>`: <t:{ts}:{i.lower()}>\n"
        message += f"`<t:{ts}:R>`: <t:{ts}:R>\n"

        await interaction.response.send_message(message, ephemeral=True)
