from redbot.core.bot import Red
from redbot.core.utils import get_end_user_data_statement_or_raise

from .ping import Ping

__red_end_user_data_statement__ = (
    "This cog does not persistently store data or metadata about users."
)

async def setup(bot: Red) -> None:
    await bot.add_cog(Ping(bot))