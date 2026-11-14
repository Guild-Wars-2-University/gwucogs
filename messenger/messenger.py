import re
from enum import Enum

#testing redbot
import discord
from redbot.core import commands, app_commands

from common.globals import Config as global_config

class ChannelTypes(Enum):
    Message = 1
    Thread = 2

VALID_MESSAGE_CHANNEL_TYPES = discord.TextChannel | discord.StageChannel | discord.VoiceChannel | discord.Thread
VALID_THREAD_CHANNEL_TYPES = discord.TextChannel | discord.StageChannel | discord.VoiceChannel | discord.ForumChannel
DISCORD_MESSAGE_LINK_PATTERN = r"https://discord\.com/channels/(\d+)/(\d+)/(\d+)"
DISCORD_CHANNEL_LINK_PATTERN = r"https://discord\.com/channels/(\d+)/(\d+)"

class Messenger(commands.Cog):

    STICKY_CHANNELS_CONFIG = "STICKY_CHANNELS"
    STICKY_CHANNELS = []

    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot
        Messenger.STICKY_CHANNELS = global_config.get_config(Messenger.STICKY_CHANNELS_CONFIG)

    ## MESSENGER COMMAND GROUP
    messenger_commands = app_commands.Group(name="messenger", description="Send, copy, edit, etc. bot messages")
    
    ## New Message command
    @messenger_commands.command(name="new", description="Send a new..")
    @app_commands.choices(type=[
        app_commands.Choice(name=channeltype.name, value=channeltype.value)
        for channeltype in ChannelTypes
    ])
    @app_commands.describe(
        destination_channel="Select, or enter the ID, of the destination channel",
        type="Type of message",
        message="Message or Discord message link to copy",
        title="Title of the thread"
    )
    async def new(
        self,
        interaction: discord.Interaction,
        type: app_commands.Choice[int],
        destination_channel: discord.abc.GuildChannel | discord.Thread,
        message: app_commands.Range[str, 1, 2000] | None,
        title: app_commands.Range[str, 1, 100] | None,
        attachment: discord.Attachment | None
    ) -> None:

        await interaction.response.defer(ephemeral=True)

        if not message and not attachment:
            return await interaction.followup.send("No message or file provided.", ephemeral=True)
        
        file = await attachment.to_file() if attachment else None
        is_discordlink = re.fullmatch(DISCORD_MESSAGE_LINK_PATTERN, message) if message else None

        try:
            if is_discordlink:
                channel = self.bot.get_channel(int(is_discordlink.group(2))) or await self.bot.fetch_channel(int(is_discordlink.group(2)))
                if not channel:
                    return await interaction.followup.send(f"Invalid channel ID in discord link: {is_discordlink.group(2)}", ephemeral=True)
                try:
                    message = (await channel.fetch_message(int(is_discordlink.group(3)))).content
                except Exception as e:
                    return await interaction.followup.send(f"Invalid message ID ({is_discordlink.group(3)}) in discord link: {e}", ephemeral=True)
            if message and len(message) > 2000:
                return await interaction.followup.send(f"Message exceeds 2000 character limit: {len(message)}", ephemeral=True)
            if type.value == ChannelTypes.Message.value:
                if not isinstance(destination_channel, VALID_MESSAGE_CHANNEL_TYPES):
                    return await interaction.followup.send(f"Invalid channel type for {ChannelTypes.Message.name}", ephemeral=True)
                new_message = await destination_channel.send(content=message, file=file)
                await interaction.followup.send(f"Message created: {new_message.jump_url}")
            elif type.value == ChannelTypes.Thread.value:
                if not isinstance(destination_channel, VALID_THREAD_CHANNEL_TYPES):
                    return await interaction.followup.send(f"Invalid channel type for {ChannelTypes.Thread.name}", ephemeral=True)
                if not title:
                    return await interaction.followup.send("Title required for threads.", ephemeral=True)
                if isinstance(destination_channel, discord.ForumChannel):
                    if file:
                        new_message = await destination_channel.create_thread(name=title, content=message, file=file)
                    else:
                        new_message = await destination_channel.create_thread(name=title, content=message)
                    await interaction.followup.send(f"Message created: {new_message.thread.jump_url}")
                else:
                    new_message = await destination_channel.create_thread(name=title)
                    await new_message.send(content=message, file=file)
                    await interaction.followup.send(f"Message created: {new_message.jump_url}")
            else:
                await interaction.followup.send(f"Invalid Type chosen.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

    ## Edit Message command
    @messenger_commands.command(name="edit", description="Edit a..")
    @app_commands.describe(
        old_message="Message to edit",
        message="New message or Discord message link to copy",
        title="New title of the thread"
    )
    async def edit(
        self,
        interaction: discord.Interaction,
        old_message: app_commands.Range[str, 1, 2000],
        message: app_commands.Range[str, 1, 2000] | None,
        title: app_commands.Range[str, 1, 100] | None
    ) -> None:
        
        await interaction.response.defer(ephemeral=True)

        if not title and not message:
            return await interaction.followup.send("No message or title provided")

        is_discordlink = re.fullmatch(DISCORD_MESSAGE_LINK_PATTERN, message) if message else None
        is_old_discordlink = re.fullmatch(DISCORD_MESSAGE_LINK_PATTERN, old_message)
        is_old_channellink = re.fullmatch(DISCORD_CHANNEL_LINK_PATTERN, old_message)

        if is_old_discordlink and not message:
            return await interaction.followup.send("No message provided")

        try:
            if is_discordlink:
                new_channel = self.bot.get_channel(int(is_discordlink.group(2))) or await self.bot.fetch_channel(int(is_discordlink.group(2)))
                if not new_channel:
                    return await interaction.followup.send(f"Invalid channel ID in new message discord link: {is_discordlink.group(2)}", ephemeral=True)
                try:
                    message_object = (await new_channel.fetch_message(int(is_discordlink.group(3))))
                    if message_object.author != self.bot.user:
                        return await interaction.followup.send("New message author is not Bot")
                    message = message_object.content
                except Exception as e:
                    return await interaction.followup.send(f"Invalid message ID ({is_discordlink.group(3)}) in new discord link: {e}", ephemeral=True)
            if is_old_discordlink:
                old_channel = self.bot.get_channel(int(is_old_discordlink.group(2))) or await self.bot.fetch_channel(int(is_old_discordlink.group(2)))
                if not old_channel:
                    return await interaction.followup.send(f"Invalid channel ID in old message discord link: {is_old_discordlink.group(2)}", ephemeral=True)
                try:
                    old_message_object = (await old_channel.fetch_message(int(is_old_discordlink.group(3))))
                    if old_message_object.author != self.bot.user:
                        return await interaction.followup.send("Old message author is not Bot")
                    old_message = old_message_object.content
                except Exception as e:
                    return await interaction.followup.send(f"Invalid message ID ({is_discordlink.group(3)}) in new discord link: {e}", ephemeral=True)
                
            if message and len(message) > 2000:
                return await interaction.followup.send(f"New message exceeds 2000 character limit: {len(message)}", ephemeral=True)
            if old_message and len(old_message) > 2000:
                return await interaction.followup.send(f"Old message exceeds 2000 character limit: {len(old_message)}", ephemeral=True)
            
            if message and old_message_object:
                await old_message_object.edit(content=message)

            if is_old_channellink:
                if title:
                    old_channel = self.bot.get_channel(int(is_old_channellink.group(2))) or await self.bot.fetch_channel(int(is_old_channellink.group(2)))
                    if not old_channel:
                        return await interaction.followup.send(f"Invalid channel ID in old message discord link: {is_old_discordlink.group(2)}", ephemeral=True)
                    if old_channel.owner != self.bot.user:
                        return await interaction.followup.send("Thread author is not Bot")
                    if isinstance(old_channel, discord.Thread):
                        await old_channel.edit(name=title)
        except Exception as e:
            return await interaction.followup.send(f"Error: {e}", ephemeral=True)

        return await interaction.followup.send("Message edits complete", ephemeral=True)

    ## Sticky Message command
    @messenger_commands.command(name="sticky", description="Sticky a channel")
    @app_commands.describe(
        channel="Channel to sticky or unsticky"
    )
    async def sticky(self, interaction: discord.Interaction, channel: discord.TextChannel) -> None:
        Messenger.STICKY_CHANNELS = global_config.get_config(Messenger.STICKY_CHANNELS_CONFIG)
        if not isinstance(Messenger.STICKY_CHANNELS, list):
            return await interaction.response.send_message(f"Config key {Messenger.STICKY_CHANNELS_CONFIG} is broken.", ephemeral=True)
        if channel.id in Messenger.STICKY_CHANNELS:
            Messenger.STICKY_CHANNELS.remove(channel.id)
            await interaction.response.send_message(f"Unstickied channel {channel.name}.", ephemeral=True)
        else:
            Messenger.STICKY_CHANNELS.append(channel.id)
            await interaction.response.send_message(f"Stickied channel {channel.name}.", ephemeral=True)
        global_config.set_config(Messenger.STICKY_CHANNELS_CONFIG, str(Messenger.STICKY_CHANNELS))
        return

    ## Sticky Listener
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        if message.author.bot:
            return
        if int(message.channel.id) not in Messenger.STICKY_CHANNELS:
            return
        async for bot_message in message.channel.history(limit=100):
            if bot_message.author == self.bot.user:
                content = bot_message.content
                await bot_message.delete()
                return await message.channel.send(content)
        return
