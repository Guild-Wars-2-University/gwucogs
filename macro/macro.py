import discord
from redbot.core import commands, app_commands

from common.globals import Config as global_config
from common.pagination import PaginationView

class Macro(commands.Cog):

    MACRO_CHANNEL_ID_CONFIG = "MACRO_CHANNEL_ID"
    MACRO_CHANNEL_ID = None
    MACRO_CHANNEL_THREADS = None

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        Macro.MACRO_CHANNEL_ID = global_config.get_config(Macro.MACRO_CHANNEL_ID_CONFIG)

    async def cog_load(self):
        await self.update_macro_list()

    async def update_macro_list(self):
        macro_channel = self.bot.get_channel(Macro.MACRO_CHANNEL_ID) or await self.bot.fetch_channel(Macro.MACRO_CHANNEL_ID)
        threads = macro_channel.threads
        async for thread in macro_channel.archived_threads(limit=None):
            threads.append(thread)
        Macro.MACRO_CHANNEL_THREADS = threads

    ## Macro name autocompletes
    async def macro_autocomplete(self, interaction:discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        choices = [
            app_commands.Choice(name=thread.name, value=str(thread.id))
            for thread in Macro.MACRO_CHANNEL_THREADS
            if current.lower() in thread.name.lower()
        ]
        return choices[:25]


    ## Macro Command group
    macro_commands = app_commands.Group(name="macro", description="Send custom macro responses")

    ## List Macros Command test
    @macro_commands.command(name="list", description="Lists all macro responses")
    async def list_macros(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        macro_list = [f"{thread.name} - {(await thread.fetch_message(thread.id)).content}" for thread in Macro.MACRO_CHANNEL_THREADS]

        view = PaginationView(interaction=interaction, items=macro_list, title="List of Macro Items")
        embed = view.create_embed()
        
        return await interaction.followup.send(embed=embed, view=view, ephemeral=True)

    ## Display macro command
    @macro_commands.command(name="display", description="Posts the chosen macro")
    @app_commands.autocomplete(macro=macro_autocomplete)
    async def display(self, interaction: discord.Interaction, macro: str) -> None:
        macro_channel = next((thread for thread in Macro.MACRO_CHANNEL_THREADS if str(thread.id) == macro or thread.name.lower() == macro.lower()), None)
        # macro_channel = None
        # for thread in Macro.MACRO_CHANNEL_THREADS:
        #     if str(thread.id) == macro or thread.name.lower() == macro.lower():
        #         macro_channel = thread
        #         break
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

    ## Listeners

    ## Update Macro list on ready, creation, or deletion

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        await self.update_macro_list()
    
    @commands.Cog.listener()
    async def on_thread_create(self, thread: discord.Thread) -> None:
        if thread.parent_id == Macro.MACRO_CHANNEL_ID:
            await self.update_macro_list()

    @commands.Cog.listener()
    async def on_thread_delete(self, thread: discord.Thread) -> None:
        if thread.parent_id == Macro.MACRO_CHANNEL_ID:
            await self.update_macro_list()
