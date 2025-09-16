import discord
from redbot.core import commands
from .selection import generate_optimized_team, generate_multiple_teams
from .utils import *

class PartyBuilderView(discord.ui.View):
    def __init__(self, bot:commands.Bot, interaction:discord.Interaction, message: discord.Message, react_data, role_sets, role_emoji, priority_emoji):
        super().__init__()
        self.bot = bot
        self.original_interaction = interaction
        self.original_message = message
        self.react_data = react_data
        self.role_sets = role_sets
        self.role_emoji = role_emoji
        self.role_emoji_inverse = {v: k for k, v in role_emoji.items()}
        self.priority_emoji = priority_emoji
        self.select_roleset.options = [discord.SelectOption(label=k, value=k, description=v['description']) for k, v in self.role_sets.items()]

        self.compositions = None

    def create_embed(self, comps):
        embed = None
        if comps:
            embed = discord.Embed(title="Squad Composition")

            i = 0;
            for comp in comps:
                comp_inverse = self.invert_comp(comp)
                i += 1
                embed.add_field(
                    name=f"Squad {i}",
                    value="\n".join(self.create_listing(comp_inverse)),
                    inline=False)

        return embed

    def invert_comp(self, comp):
        comp_inverse = None
        if comp:
            comp_inverse = {}
            for player, roles in comp.items():
                for role in roles:
                    comp_inverse.setdefault(role, []).append(player)

        return comp_inverse

    def create_listing(self, comp_inverse):
        return [f"{self.role_emoji_inverse[r]} {r}: " + " ".join([pl.mention for pl in p]) for r, p in comp_inverse.items()]

    @discord.ui.select(placeholder="Select Composition", min_values=1, max_values=1)
    async def select_roleset(self, interaction: discord.Interaction, select: discord.ui.Select):
        for opt in select.options:
            opt.default = opt.value in select.values
        
        if select.values:
            val = select.values[0]

            self.add_reactions_button.disabled = False

            inverse = {}
            for k, v in self.react_data.items():
                key = str(k)
                if key in self.priority_emoji:
                    for x in v:
                        d = inverse.setdefault(x, {})
                        d['priority'] = self.priority_emoji[key]
                        d.setdefault('roles', [])
                if key in self.role_emoji:
                    for x in v:
                        d = inverse.setdefault(x, {})
                        d.setdefault('priority', 1)
                        d.setdefault('roles', []).append(self.role_emoji[key])

            role_set = self.role_sets[val]
            self.compositions, unused = generate_multiple_teams(inverse, role_set)
            
            embed = None
            if self.compositions:
                embed = self.create_embed(self.compositions);
                self.ping_in_thread_button.disabled = False
            else:
                self.ping_in_thread_button.disabled = True
        else:
            self.add_reactions_button.disabled = True
            
        await interaction.response.edit_message(view=self, embed=embed)
        
    @discord.ui.button(label="Ping Selected in Thread", style=discord.ButtonStyle.green, row=2, disabled=True)
    async def ping_in_thread_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        thread = self.original_message.thread
        if not thread:
            default_name = generate_default_thread_name(self.original_message, "New Thread")
            thread = await self.original_message.create_thread(name=default_name)

        n = 1;
        content = []

        for comp in self.compositions:
            content.append(f"### Squad {n} Composition:")
            inv_comp = self.invert_comp(comp)
            content.extend(self.create_listing(inv_comp))

        await thread.send(content="\n".join(content))
        await interaction.response.edit_message(delete_after=0)
        self.stop()
        
    @discord.ui.button(label="Add Reactions", style=discord.ButtonStyle.blurple, row=2, disabled=True)
    async def add_reactions_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        await interaction.response.edit_message(delete_after=0)
        self.stop()

        emoji_for_comp = []
        if self.select_roleset.values:
            emoji_for_comp.extend(self.priority_emoji.keys())
            selected_role = self.select_roleset.values[0]
            role_set = self.role_sets[selected_role]
            all_roles = [k for k in role_set.get('roles', {}).keys()] + [k for k in role_set.get('special_roles', {}).keys()]
            emoji_for_comp.extend([self.role_emoji_inverse[r] for r in all_roles])

        for emoji in emoji_for_comp:
            await self.original_message.add_reaction(emoji)