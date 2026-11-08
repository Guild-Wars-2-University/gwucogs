import discord
from redbot.core import commands, app_commands

from common.globals import Config as global_config
from common.pagination import PaginationView

class Macro(commands.Cog):

    MACRO_CHANNEL_ID = None
    MACRO_CHANNEL_ID_CONFIG = "MACRO_CHANNEL_ID"

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        Macro.MACRO_CHANNEL_ID = global_config.get_config(Macro.MACRO_CHANNEL_ID_CONFIG)

    ## Macro name autocompletes
    async def macro_autocomplete(self, interaction:discord.Interaction, current: str) -> list[app_commands.Choice[str]]:

        macro_channel = self.bot.get_channel(Macro.MACRO_CHANNEL_ID) or await self.bot.fetch_channel(Macro.MACRO_CHANNEL_ID)

        choices = [
            app_commands.Choice(name=thread.name, value=str(thread.id))
            for thread in macro_channel.threads
            if current.lower() in thread.name.lower()
        ]
        return choices[:25]


    ## Macro Command group
    macro_commands = app_commands.Group(name="macro", description="Send custom macro responses")

    ## List Macros Command test
    @macro_commands.command(name="list", description="Lists all macro responses")
    async def list_macros(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        macro_channel = self.bot.get_channel(Macro.MACRO_CHANNEL_ID) or await self.bot.fetch_channel(Macro.MACRO_CHANNEL_ID)
        
        if not macro_channel:
            return await interaction.followup.send("Macro channel not found", ephemeral=True)
        
        threads = macro_channel.threads

        async for thread in macro_channel.archived_threads(limit=None):
            threads.append(thread)

        macro_list = [f"{thread.name} - {(await thread.fetch_message(thread.id)).content}" for thread in threads]

        view = PaginationView(interaction=interaction, items=macro_list, title="List of Macro Items")
        embed = view.create_embed()
        
        return await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    ## Display macro command
    @macro_commands.command(name="display", description="Posts the chosen macro")
    @app_commands.autocomplete(macro=macro_autocomplete)
    async def display(self, interaction: discord.Interaction, macro: str) -> None:
        
        try:
            macro_channel = self.bot.get_channel(macro) or await self.bot.fetch_channel(macro)
        except:
            macro_channel = None
        if not macro_channel:
            return await interaction.response.send_message("Macro not found.", ephemeral=True) 
                             
        messages = [message async for message in macro_channel.history(oldest_first=True, limit=None)]
        messages = messages[1:]

        await interaction.response.send_message(f"Displaying the macro {macro_channel.name} below!")

        for message in messages:
            await interaction.channel.send(message.content)
            if message.attachments:
                for attachment in message.attachments:
                    await interaction.channel.send(attachment)
        return