import discord
from discord.ext import commands

from .macro import Macro

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Macro(bot))