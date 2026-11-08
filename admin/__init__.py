import discord
from discord.ext import commands

from .admin import Admin

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Admin(bot))