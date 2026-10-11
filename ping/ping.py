from enum Import Enum

import discord
from redbot.core import commands, app_commands

class PingUsersModal(discord.ui.Modal, title="Ping users"):
    ping_type = discord.ui.Label(
        text="Ping users by",
        component=discord.ui.Select(
            options=[
                discord.SelectOption(
                    label="Reacts",
                    value=PingTypes.Reacts.value
                ),
                discord.SelectOption(
                    label="Mentions",
                    value=PingTypes.Mentions.value
                )
            ],
            placeholder="Select an option",
            required=True
        )
    )
    user_message = discord.ui.Label(
        text="Optional Message",
        component=discord.ui.TextInput(
            style=discord.TextStyle.paragraph,
            max_length=1500,
            required=False
        )
    )

    def __init__(self, message: discord.Message):
        super().__init__()
        self.message = message

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        message = self.message

        try:
            if (int(self.ping_type.component.values[0]) == PingTypes.Reacts.value):
                if message.reactions:
                    users = set()
                    for reaction in message.reactions:
                        async for user in reaction.users():
                            if not user.bot:
                                users.add(user.mention)
                    users_string = ' '.join(str(user) for user in users)
                else:
                    await interaction.followup.send("No users reacted.", ephemeral=True)
                    return
            elif (int(self.ping_type.component.values[0]) == PingTypes.Mentions.value):
                if message.mentions:
                    users_string = ' '.join(user.mention for user in message.mentions)
                else:
                    await interaction.followup.send("No users to ping.", ephemeral=True)
                    return

            if ((len(users_string) + len(self.user_message.component.value)) > 2000):
                await interaction.followup.send("Overall message length too long.", ephemeral=True)
                return

            if message.thread:
                await message.thread.send(content=users_string + '\n' + self.user_message.component.value)
                await interaction.followup.send("Pinged users in thread.", ephemeral=True)
            else:
                await message.channel.send(content=users_string + '\n' + self.user_message.component.value)
                await interaction.followup.send("Pinged users here.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Error: {e}", ephemeral=True)



class Ping(commands.Cog):
    def __init__(self, bot:commands.Bot) -> None:
        self.bot = bot

        self.ctx_menu_ping_users =app_commands.ContextMenu(
            name="Ping Users",
            callback=self.ping_users
        )

        self.bot.tree.add_command(self.ctx_menu_ping_users)


    async def ping_users(self, interaction:discord.Interaction, message: discord.Message) -> None:
        ping_users_modal = PingUsersModal(message=message)

        await interaction.response.send_modal(ping_users_modal)
