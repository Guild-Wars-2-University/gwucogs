import discord
from redbot.core import commands, app_commands

class PingReactsModal(discord.ui.Modal, title="Ping Reacts"):
    user_message = discord.ui.TextInput(
        label="Optional Message",
        style=discord.TextStyle.paragraph,
        required=False
    )

    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        message = self.message

        try:
            if message.reactions:
                users = []
                for reaction in message.reactions:
                    async for user in reaction.users():
                        if not user.bot and user not in users:
                            users.append(user)
                users_string = ' '.join(user.mention for user in users)
                if message.thread:
                    await message.thread.send(content=users_string + '\n' + self.user_message.value)
                    await interaction.followup.send("Pinged users in thread.", ephemeral=True)
                else:
                    await message.channel.send(content=users_string + '\n' + self.user_message.value)
                    await interaction.followup.send("Pinged users here.", ephemeral=True)
            else:
                await interaction.followup.send("No users reacted.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)

class PingChosenModal(discord.ui.Modal, title="Ping Chosen"):
    user_message = discord.ui.TextInput(
        label="Optional Message",
        style=discord.TextStyle.paragraph,
        required=False
    )

    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        message = self.message

        try:
            if message.mentions:
                users_string = ' '.join(user.mention for user in message.mentions)
                if message.thread:
                    await message.thread.send(content=users_string + '\n' + self.user_message.value)
                    await interaction.followup.send("Pinged users in thread.", ephemeral=True)
                else:
                    await message.channel.send(content=users_string + '\n' + self.user_message.value)
                    await interaction.followup.send("Pinged users here.", ephemeral=True)
            else:
                await interaction.followup.send("No users to ping.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)


class Ping(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

        self.ctx_menu_ping_reacts = app_commands.ContextMenu(
            name="Ping Reacts",
            callback=self.ping_reacts
        )

        self.ctx_menu_ping_chosen = app_commands.ContextMenu(
            name="Ping Chosen",
            callback=self.ping_chosen
        )

        self.bot.tree.add_command(self.ctx_menu_ping_reacts)
        self.bot.tree.add_command(self.ctx_menu_ping_chosen)


    async def ping_reacts(self, interaction: discord.Interaction, message: discord.Message) -> None:
        ping_reacts_modal = PingReactsModal(message=message)

        await interaction.response.send_modal(ping_reacts_modal)

    async def ping_chosen(self, interaction: discord.Interaction, message: discord.Message) -> None:
        ping_chosen_modal = PingChosenModal(message=message)

        await interaction.response.send_modal(ping_chosen_modal)
