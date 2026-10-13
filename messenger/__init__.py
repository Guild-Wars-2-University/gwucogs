import discord
from discord.ext import commands

from .messenger import Messenger

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Messenger(bot))