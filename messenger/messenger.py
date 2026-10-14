import re

import discord
from redbot.core import commands, app_commands

valid_message_channel_types = discord.TextChannel | discord.StageChannel | discord.VoiceChannel | discord.Thread
valid_thread_channel_types = discord.TextChannel | discord.StageChannel | discord.VoiceChannel | discord.ForumChannel
discord_message_link_pattern = r"https://discord\.com/channels/(\d+)/(\d+)/(\d+)"

class Messenger(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

    ## MESSENGER COMMAND GROUP
    messenger_commands = app_commands.Group(name="messenger", description="Send, copy, edit, etc. bot messages")

    ## New Message command
    @messenger_commands.command(name="new", description="Send a new message")
    @app_commands.describe(
        destination_channel="Select, or enter the ID, of the destination channel",
        message="Message or Discord message link to copy"
    )
    async def new(
        self,
        interaction: discord.Interaction,
        destination_channel: valid_message_channel_types,
        message: app_commands.Range[str, 1, 2000]
    ) -> None:
        

        is_discordlink = re.search(discord_message_link_pattern, message)

        try:
            if is_discordlink:
                channel = self.bot.get_channel(int(is_discordlink.group(2)))
                if not channel:
                    return await interaction.response.send_message(f"Invalid channel ID in discord link: {is_discordlink.group(2)}", ephemeral=True)
                try:
                    message = (await channel.fetch_message(int(is_discordlink.group(3)))).content
                except Exception as e:
                    return await interaction.response.send_message(f"Invalid message ID ({is_discordlink.group(3)}) in discord link: {e}", ephemeral=True)
            if len(message) > 2000:
                return await interaction.response.send_message(f"Message exceeds 2000 character limit: {len(message)}", ephemeral=True)
            new_message = await destination_channel.send(content=message)
            await interaction.response.send_message(f"Message created: {new_message.jump_url}")
        except Exception as e:
            await interaction.response.send_message(f"Error: {e}", ephemeral=True)