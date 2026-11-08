import discord
from redbot.core import commands, app_commands

from common.globals import CONFIG_FILE
from common.globals import Config as global_config

class Admin(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    ## ADMIN COMMAND GROUP
    admin_commands = app_commands.Group(name="admin", description="Adminster bot")

    ## Get New Mentions
    @admin_commands.command(name='getmentions', description="Get mentions since last time")
    async def newmentions(self, interaction: discord.Interaction) -> None:
        mentions = []
        async for message in interaction.channel.history(limit=None):
            if message.author.id == self.bot.user.id:
                break
            for user in message.mentions:
                current_user = interaction.guild.get_member(int(user.id))
                if not current_user:
                    try:
                        current_user = await interaction.guild.fetch_member(int(user.id))
                        mentions.append(user.mention)
                    except discord.NotFound:
                        continue
        mentions_string = " ".join(mentions)
        if mentions_string:
            return await interaction.response.send_message(mentions_string)
        else:
            return await interaction.response.send_message("No mentions found.", ephemeral=True)

    ## Sync Slash Commands command
    @admin_commands.command(name="sync", description="Sync slash commands")
    async def sync(self, interaction:discord.Interaction) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            await self.bot.tree.sync(guild=interaction.guild)
            await interaction.followup.send("Slash commands synced!")
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    ## ADMIN CONFIG SUBCOMMAND GROUP
    config_admin_commands = app_commands.Group(name="config", description="Administer config", parent=admin_commands)

    ## Setup Config file command
    @config_admin_commands.command(name="create", description="Creates config file")
    async def create_config(self, interaction:discord.Interaction) -> None:
        if CONFIG_FILE.exists():
            return await interaction.response.send_message("Config file already exists.")
        try:
            CONFIG_FILE.touch()
            return await interaction.response.send_message("Created config file.")
        except Exception as e:
            return await interaction.response.send_message("Error: {e}")

    ## List Config command

    ## Get config variable command
    @config_admin_commands.command(name="get", description="Get a config variable")
    async def get_config(self, interaction:discord.Interaction, key:str)-> None:
        config_data = global_config.get_config(key)
        if not config_data:
            return await interaction.response.send_message(f"Key {key} not found.", ephemeral=True)
        return await interaction.response.send_message(f"Get {key} : {config_data}", ephemeral=True)

    ## Set config variable command
    @config_admin_commands.command(name="set", description="Set a config variable")
    async def set_config(self, interaction:discord.Interaction, key:str, value:str)-> None:
        config_data = global_config.set_config(key, value)
        if config_data:
            return await interaction.response.send_message(config_data, ephemeral=True)
        return await interaction.response.send_message(f"Set {key} : {value}", ephemeral=True)

    ## Delete config variable command
    @config_admin_commands.command(name="delete", description="Get a config variable")
    async def delete_config(self, interaction:discord.Interaction, key:str)-> None:
        config_data = global_config.delete_config(key)
        if config_data:
            return await interaction.response.send_message(config_data, ephemeral=True)
        return await interaction.response.send_message(f"Deleted {key}", ephemeral=True)

    ## ADMIN COG SUBCOMMAND GROUP
    cog_admin_commands = app_commands.Group(name="cog", description="Administer cogs", parent=admin_commands)

    ## Load Cog command
    @cog_admin_commands.command(name="load", description="Load a cog")

    async def load(self, interaction:discord.Interaction, cog:str) -> None:
        try:
            await self.bot.load_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"{cog} has been loaded!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    ## Reload Cog command
    @cog_admin_commands.command(name="reload", description="Reload a cog")

    async def reload(self, interaction:discord.Interaction, cog:str) -> None:
        try:
            await self.bot.reload_extension(f"cogs.{cog}")
            
            await interaction.response.send_message(f"{cog} has been reloaded!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)

    ## Unload Cog command
    @cog_admin_commands.command(name="unload", description="Unload a cog")

    async def unload(self, interaction:discord.Interaction, cog:str) -> None:
        try:
            await self.bot.unload_extension(f"cogs.{cog}")
            await interaction.response.send_message(f"{cog} has been unloaded!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)