import math

import discord

class PaginationView(discord.ui.View):
    def __init__(self, interaction: discord.Interaction, items: list, title: str, items_per_page: int = 10):
        super().__init__(timeout=180)
        self.interaction = interaction
        self.items = items
        self.title = title
        self.items_per_page = items_per_page
        self.current_page = 0
        self.total_pages = math.ceil(len(items) / items_per_page) or 1

    async def interaction_check(self, interaction:discord.Interaction) -> bool:
        if interaction.user != self.interaction.user:
            await interaction.response.send_message("Only the author can use these buttons", ephemeral=True)
            return False
        return True

    async def on_timeout(self):
        await self.interaction.edit_original_response(view=None)

    def create_embed(self) -> discord.Embed:
        start_item = self.current_page * self.items_per_page
        end_item = start_item + self.items_per_page
        page_items = self.items[start_item:end_item]

        description = "\n".join(f"{item}" for item in page_items)

        embed = discord.Embed(
            title=self.title,
            description=description or "Nothing to display.",
            color=discord.Color.dark_orange()
        )
        embed.set_footer(text=f"Page {self.current_page + 1} of {self.total_pages}")
        self.update_buttons()
        return embed

    def update_buttons(self):
        self.first_button.disabled = self.previous_button.disabled = self.current_page == 0
        self.next_button.disabled = self.last_button.disabled = self.current_page == self.total_pages - 1

    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.primary)
    async def first_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        self.current_page = 0
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(emoji="◀️", style=discord.ButtonStyle.primary)
    async def previous_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        if self.current_page > 0:
            self.current_page -= 1
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(emoji="▶️", style=discord.ButtonStyle.primary)
    async def next_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
        await interaction.response.edit_message(embed=self.create_embed(), view=self)

    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.primary)
    async def last_button(self, interaction:discord.Interaction, button: discord.ui.Button):
        self.current_page = self.total_pages - 1
        await interaction.response.edit_message(embed=self.create_embed(), view=self)