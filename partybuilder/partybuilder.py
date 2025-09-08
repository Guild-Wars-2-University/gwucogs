from dis import disco
from typing import Literal, Dict, List, Generator, Union, Callable, Self, Awaitable
from sys import maxsize
from asyncio import sleep

import emoji
import re
import discord
from random import Random, randrange
from itertools import islice
from collections import OrderedDict
from datetime import datetime

from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.config import Config
from redbot.core.utils import bounded_gather

from .partybuilderview import PartyBuilderView
from .utils import *

RequestType = Literal["discord_deleted_user", "owner", "user", "user_strict"]

invisible = '\u200b'


class InputBox(discord.ui.Modal):
    def __init__(self, title:str, inpurName:str, on_submit:Callable[[discord.Interaction, Self], Awaitable]):
        super().__init__(title=title)
        self.callback = on_submit
        self.input_box = discord.ui.TextInput(label=inpurName, style=discord.TextStyle.short)
        self.add_item(self.input_box)

    async def on_submit(self, interaction: discord.Interaction):
        await self.callback(interaction, self)
        #await interaction.response.send_message(f'{self.input_box}', ephemeral=True)

class PartyBuilderCog(commands.Cog):
    """GWU partybuilder Cog"""

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.key = 124374143
        self.config = Config.get_conf(self, self.key, force_registration=True)

        default_global = {
            'priority_emoji' : {
                '<:quaggan_happy:794988733437968384>' : 0,
                '<:choya_angry:788250619810414592>' : 1,
            },
            'role_emoji' : {
                '<:B_alacrity:768642052124573749>' : 'adps',
                '<:B_quickness:768642112740524062>' : 'qdps',
                '<:B_AlacHeal:1007268338570899476>' : 'aheal',
                '<:B_QuickHeal:1007268340793884713>' : 'qheal',
                '⚔️' : 'dps',
                '🔥' : 'condi',
                '🪞' : 'reflect',
                '<:P8_chronomancer:774783646241783808>' : 'tower',
                '🖐️' : 'handkite',
                '📌' : 'tdpush',
                '🪔' : 'lamp',
                '🪁' : 'qadimkite',
                '🗼' : 'pylon',
                '<:T_arrow:768660871719026708>' : 'aranged',
                '<:T_circle:768660920289198081>' : 'qranged',
                '🏹' : 'ranged'
            },
            'role_attributes': [
                'dps',
                'heal',
                'quick',
                'alac'
            ],
            'rolesets' : {

                'Standard 5 Player': {
                    'players': 5,
                    'description': 'Standard 5-player squad.',
                    'attributes': {
                        'dps': 4,
                        'heal': 1,
                        'quick': 1,
                        'alac': 1
                    },
                    'roles': {
                        'aheal': ['alac', 'heal'],
                        'qheal': ['quick', 'heal'],
                        'adps': ['alac', 'dps'],
                        'qdps': ['quick', 'dps'],
                        'dps': ['dps']
                    }
                },

                'Standard 10 Player': {
                    'players': 10,
                    'description': 'Standard 10-player squad.',
                    'attributes': {
                        'dps': 8,
                        'heal': 2,
                        'quick': 2,
                        'alac': 2
                    },
                    'roles': {
                        'aheal': ['alac', 'heal'],
                        'qheal': ['quick', 'heal'],
                        'adps': ['alac', 'dps'],
                        'qdps': ['quick', 'dps'],
                        'dps': ['dps']
                    }
                },

                'Raid - Wing 1': {
                    'players': 10,
                    'description': 'Raid squad with condi dps.',
                    'attributes': {
                        'dps': 8,
                        'heal': 2,
                        'quick': 2,
                        'alac': 2,
                        'condi': 2
                    },
                    'roles': {
                        'aheal': ['alac', 'heal'],
                        'qheal': ['quick', 'heal'],
                        'adps': ['alac', 'dps'],
                        'qdps': ['quick', 'dps'],
                        'dps': ['dps'],
                        'condi': ['condi','dps']
                    }
                },

                'Raid - Wing 4': {
                    'players': 10,
                    'description': 'Raid squad with handkite.',
                    'attributes': {
                        'dps': 8,
                        'heal': 2,
                        'quick': 2,
                        'alac': 2,
                        'handkite': 1
                    },
                    'roles': {
                        'aheal': ['alac', 'heal'],
                        'qheal': ['quick', 'heal'],
                        'adps': ['alac', 'dps'],
                        'qdps': ['quick', 'dps'],
                        'dps': ['dps'],
                        'handkite': ['handkite','dps']
                    }
                },


                'Raid - Wing 5': {
                    'players': 10,
                    'description': 'Raid squad with tdpush.',
                    'attributes': {
                        'dps': 8,
                        'heal': 2,
                        'quick': 2,
                        'alac': 2,
                        'tdpush': 1
                    },
                    'roles': {
                        'aheal': ['alac', 'heal'],
                        'qheal': ['quick', 'heal'],
                        'adps': ['alac', 'dps'],
                        'qdps': ['quick', 'dps'],
                        'dps': ['dps'],
                        'tdpush': ['tdpush','dps']
                    }
                },

                'Raid - Wing 6': {
                    'players': 10,
                    'description': 'Raid squad with lamp & qadim kite.',
                    'attributes': {
                        'dps': 8,
                        'heal': 2,
                        'quick': 2,
                        'alac': 2,
                        'lamp': 1,
                        'qadimkite': 1
                    },
                    'roles': {
                        'aheal': ['alac', 'heal'],
                        'qheal': ['quick', 'heal'],
                        'adps': ['alac', 'dps'],
                        'qdps': ['quick', 'dps'],
                        'dps': ['dps'],
                        'lamp': ['lamp','dps'],
                        'qadimkite': ['qadimkite','dps']
                    }
                },

                'Raid - Wing 7': {
                    'players': 10,
                    'description': 'Raid squad with pylon.',
                    'attributes': {
                        'dps': 8,
                        'heal': 2,
                        'quick': 2,
                        'alac': 2,
                        'pylon': 3
                    },
                    'roles': {
                        'aheal': ['alac', 'heal'],
                        'qheal': ['quick', 'heal'],
                        'adps': ['alac', 'dps'],
                        'qdps': ['quick', 'dps'],
                        'dps': ['dps'],
                        'pylon': ['pylon','dps']
                    }
                },
            }
        }

        self.config.register_guild(**default_global)

        self.ctx_menu_pick_from_reactions = app_commands.ContextMenu(name='Pick from reactions', callback=self.pick_from_reactions)
        self.bot.tree.add_command(self.ctx_menu_pick_from_reactions)
        
    async def cog_unload(self) -> None:
        self.bot.tree.remove_command(self.ctx_menu_pick_from_reactions.name, type=self.ctx_menu_pick_from_reactions.type)
    
    class RoleAttribute:
        def __init__(self, name:str):
            self.name:str = name
            self.required:int = 0
        
    class Role:
        def __init__(self, name:str):
            self.name:str = name
            self.attributes:set[PartyBuilderCog.RoleAttribute] = set[PartyBuilderCog.RoleAttribute]()
            self.emoji:DiscordEmoji

    class RoleBuilder(discord.ui.View):
        def __init__(self, interaction:discord.Interaction, message: discord.Message):
            super().__init__()
            self.original_interaction = interaction
            self.original_message = message
            self.has_replied = True
            self.selected:str = None
            self.attributes = OrderedDict[str, PartyBuilderCog.RoleAttribute]()
            self.remove_item(self.button_delete)
            self.remove_item(self.attribute_value_selector)
            #self.attributes.add(GWUCog.RoleAttribute("dps"))
            
            self.refresh_attribute_options()
            self.update_embed(interaction)

        async def modal_callback(self, interaction:discord.Interaction, modal:InputBox):
            if modal.input_box.value:
                self.add_attribute(modal.input_box.value)

            self.refresh_attribute_options()
            await self.update_and_send(interaction)

        def add_attribute(self, name:str):
            self.attributes[name] = GWUCog.RoleAttribute(name)

        def refresh_attribute_options(self):
            if self.attributes:
                self.attribute_selector.disabled = False
                self.attribute_selector.options = [discord.SelectOption(label=key, value=key, default=key==self.selected) for key in self.attributes.keys()]
            else:
                self.attribute_selector.disabled = True
                self.attribute_selector.options = [discord.SelectOption(label="dummy", value="dummy")]

        @discord.ui.select(placeholder="Edit attribute", min_values=0)
        async def attribute_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
            for opt in select.options:
                opt.default = opt.value in select.values
               
            if select.values:
                self.add_item(self.button_delete)
                self.selected = select.values[0]
                self.button_delete.disabled = False
                self.attribute_value_selector.options = [discord.SelectOption(label=f"{self.selected}: {i}", value=str(i), default=i==self.attributes[self.selected].required) for i in range(0, 25)]
                self.add_item(self.attribute_value_selector)
            else:
                self.remove_item(self.button_delete)
                self.selected = None
                self.button_delete.disabled = True
                self.attribute_value_selector.options = [discord.SelectOption(label="dummy", value="dummy")]
                self.remove_item(self.attribute_value_selector)

            await self.update_and_send(interaction)

        @discord.ui.button(label="Add Attribute", emoji="➕", style=discord.ButtonStyle.gray, row=3)
        async def button_add(self, interaction:discord.Interaction, button:discord.ui.Button):
            await interaction.response.send_modal(InputBox("Test Title", "test label", self.modal_callback))
            #await builder.update_and_send(interaction)
            
        @discord.ui.select(placeholder="Edit attribute", min_values=1, max_values=1)
        async def attribute_value_selector(self, interaction: discord.Interaction, select: discord.ui.Select):
            for opt in select.options:
                opt.default = opt.value in select.values
               
            if select.values:
                self.attributes[self.selected].required = select.values[0]

            await self.update_and_send(interaction)

        @discord.ui.button(label="Delete", emoji="🗑️", disabled=True, style=discord.ButtonStyle.red, row=3)
        async def button_delete(self, interaction:discord.Interaction, button:discord.ui.Button):
            if self.attributes.pop(self.selected, None):
                self.remove_item(self.button_delete)
                self.selected = None
                self.button_delete.disabled = True
                
            self.refresh_attribute_options()
            await self.update_and_send(interaction)

        def create_embed(self, interaction:discord.Interaction) -> discord.Embed:
            embed = discord.Embed()
            embed.title = f"Roles and Attributes:"
    
            max_length:int
            if self.attributes:
                max_length = max(max([len(key) for key in self.attributes.keys()]), 10)
            else:
                max_length = 10

            text = [
                "```asciidoc",
                f"{'Name':{max_length+1}} Req.",
                "\n".join([f"{'>' if attr.name == self.selected else ' '}{attr.name:{max_length}} {attr.required}" for attr in self.attributes.values()]),
                "```",
            ]

            embed.add_field(
                name=f"Attributes ({len(self.attributes)}/25)",
                value="\n".join(text))
            
            return embed

        def update_embed(self, interaction:discord.Interaction):
            self.embed = self.create_embed(interaction)

        async def update_and_send(self, interaction: discord.Interaction):
            self.update_embed(interaction)
            await self.send(interaction)

        async def send(self, interaction: discord.Interaction):
            self._refresh_timeout()

            if not self.has_replied:
                self.has_replied=True
                await interaction.followup.send(
                    embed=self.embed,
                    ephemeral=True,
                    view=self)
            else:
                await interaction.response.edit_message(
                    embed=self.embed,
                    view=self)
             
    class ReactionSendView(discord.ui.View):
        def __init__(self, bot:commands.Bot, interaction:discord.Interaction, message: discord.Message):
            super().__init__()
            self.bot = bot
            self.original_interaction = interaction
            self.original_message = message
            self.select_reactions.options = [discord.SelectOption(label=get_emoji_name(e, str(interaction.locale.value)), value=str(e), emoji=e, default=True) for e in islice(get_emojis_from_text(self.bot, message.content), 25)]
            self.select_reactions.max_values = len(self.select_reactions.options)

        @discord.ui.select(placeholder="Select Reactions", min_values=0)
        async def select_reactions(self, interaction: discord.Interaction, select: discord.ui.Select):
            for opt in select.options:
                opt.default = opt.value in select.values
               
            self.button_send.disabled = not select.values
            await interaction.response.edit_message(view=self)
            
        @discord.ui.button(label="Post Reactions", style=discord.ButtonStyle.green)
        async def button_send(self, interaction:discord.Interaction, button:discord.ui.Button):
            await interaction.response.edit_message(delete_after=0)
            self.stop()
            await bounded_gather(*[self.original_message.add_reaction(o.emoji) for o in self.select_reactions.options if o.default])

    class ReactionsPicker(discord.ui.View):
        def __init__(self, bot:commands.Bot, interaction:discord.Interaction, message: discord.Message, react_data: OrderedDict[str, List[str]]):
            super().__init__()
            self.bot = bot
            self.original_interaction = interaction
            self.original_message = message
            self.has_replied = False
            self.include_self = True
            self.react_data = react_data
            self.filter_options = set()
            
            self.emoji_picker.options = [discord.SelectOption(label=invisible, value=str(emoji), emoji=emoji) for emoji in react_data.keys()]
            self.emoji_picker.max_values = len(self.emoji_picker.options)

            self.select_number = 0
            self.number_picker_refresh()
            self.update_embed(interaction)

        def get_max_select_value(self):
            users = set()
            for emoji, mentions in self.react_data.items():
                if str(emoji) not in self.filter_options:
                    users.update(mentions)

            return len(users)

        def number_picker_refresh(self):
            max_val = self.get_max_select_value()
            numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45, 50]
            if max_val not in numbers:
                numbers.append(max_val)

            n = min(self.select_number, max_val)
            opts = [discord.SelectOption(value=str(i), label=f"Choose {i}", default=n==i) for i in numbers if i <= max_val]

            if opts and not any([o.default for o in opts]):
                opts[-1].default = True
                
            self.max_select_number = max_val
            self.select_number = n
            self.number_picker.options = opts

        @discord.ui.select(placeholder="Reactions to Ignore", min_values=0)
        async def emoji_picker(self, interaction: discord.Interaction, select: discord.ui.Select):
            for opt in select.options:
                opt.default = opt.value in select.values
                
            self.filter_options.clear()
            self.filter_options.update(select.values)
            self.number_picker_refresh()

            await self.update_and_send(interaction)

        @discord.ui.select(placeholder="Users to Select")
        async def number_picker(self, interaction: discord.Interaction, select: discord.ui.Select):
            for opt in select.options:
                opt.default = opt.value in select.values

            self.select_number = int(select.values[0]) if select.values else self.max_select_number

            await self.update_and_send(interaction)

        @discord.ui.button(label="Ping Selected in Thread", style=discord.ButtonStyle.green, row=2)
        async def ping_in_thread_button(self, interaction:discord.Interaction, button:discord.ui.Button):
            thread = self.original_message.thread
            if not thread:
                default_name = generate_default_thread_name(self.original_message, "New Thread")
                thread = await self.original_message.create_thread(name=default_name)

            embed = discord.Embed()
            embed.add_field(
                name="Selected:",
                value="\n".join([f"{m}" for m in self.users]))

            await thread.send(embed=embed)
            await interaction.response.edit_message(delete_after=0)
            self.stop()
            
        @discord.ui.button(label="✅ Include Self", row=2)
        async def include_self_button(self, interaction:discord.Interaction, button:discord.ui.Button):
            self.include_self = not self.include_self
            button.label = "✅ Include Self" if self.include_self else "🔲 Include Self"

            await self.update_and_send(interaction)

        @discord.ui.button(label="🎲 Shuffle", style=discord.ButtonStyle.gray, row=2)
        async def shuffle_button(self, interaction:discord.Interaction, button:discord.ui.Button):
            await self.update_and_send(interaction)

        # @discord.ui.button(label="?", style=discord.ButtonStyle.gray, row=3)
        # async def builder_button(self, interaction:discord.Interaction, button:discord.ui.Button):
        #     builder = GWUCog.RoleBuilder(interaction, self.original_message)
        #     await builder.update_and_send(interaction)

        def update_embed(self, interaction:discord.Interaction):
            self.embed = self.create_embed(interaction)

        def create_embed(self, interaction:discord.Interaction) -> discord.Embed:
            embed = discord.Embed()
            total = 0
            users = set()
            total_ignored = 0
            users_ignored = set()

            self_user = interaction.user.mention;

            for emoji, mentions in self.react_data.items():
                if str(emoji) in self.filter_options:
                    total_ignored += len(mentions)
                    users_ignored.update(mentions)
                else:
                    total += len(mentions)
                    users.update(mentions)
                    embed.add_field(
                        name=str(emoji),
                        value=f"> -# {len(mentions)} total\n" + "\n".join([f"> {m}" for m in mentions]))
                    
            embed.title = f"{total} Reactions from {len(users)} Users"

            if users_ignored:
                embed.description = f"Ignored {total_ignored} Reactions from {len(users_ignored)} Users"

            if self.include_self:
                users.add(self_user)
                
            n = min(len(users), self.select_number)

            disableButtons = n <= 0
            self.include_self_button.disabled = disableButtons
            self.ping_in_thread_button.disabled = disableButtons
            self.shuffle_button.disabled = disableButtons

            if users and n:
                random_selection = list()
                if self.include_self:
                    users.discard(self_user)
                    random_selection.append(self_user)
                    n -= 1

                if n > 0:
                    seed = randrange(maxsize)
                    rng = Random(seed)
                    #embed.set_footer(text=f"seed: {seed}")
                    random_selection.extend(rng.sample(sorted(users), n))

                random_selection_str = "\n".join([f"> {m}" for m in random_selection])
                include_self_str = " (Including self)" if self.include_self else ""
                embed.add_field(
                    inline=False,
                    name=f"🎲 {self.select_number} Randomly Selected{include_self_str}:",
                    value=random_selection_str)


            return embed

        async def update_and_send(self, interaction: discord.Interaction):
            self.update_embed(interaction)
            await self.send(interaction)

        async def send(self, interaction: discord.Interaction):
            if not self.has_replied:
                self.has_replied=True
                await interaction.followup.send(
                    embed=self.embed,
                    ephemeral=True,
                    view=self)
            else:
                await interaction.response.edit_message(
                    embed=self.embed,
                    view=self)

    async def pick_from_reactions(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(ephemeral=True, thinking=True)

        # react_data = OrderedDict()
        # for r in message.reactions:
        #     mentions = [u async for u in r.users() if u != self.bot.user]
        #     if mentions:
        #         react_data[r.emoji] = mentions
        react_data = await gather_reactions(message)
                
        priority_emoji = await self.config.guild(interaction.guild).get_raw('priority_emoji')
        role_emoji = await self.config.guild(interaction.guild).get_raw('role_emoji')
        rolesets = await self.config.guild(interaction.guild).get_raw('rolesets')

        view = PartyBuilderView(self.bot, interaction, message, react_data, rolesets, role_emoji, priority_emoji);
        await interaction.followup.send(view=view)

        # if react_data:
        #     role_emoji = await self.config.guild(interaction.guild).get_raw('role_emoji')
        #     rolesets = await self.config.guild(interaction.guild).get_raw('rolesets')

        #     view = PartyBuilderView(self.bot, interaction, message, react_data, rolesets, role_emoji);
        #     await interaction.followup.send(view=view)

        #     #view = GWUCog.ReactionsPicker(self.bot, interaction, message, react_data)
        #     #await view.update_and_send(interaction)
        # elif any(get_emojis_from_text(self.bot, message.content)):
        #     await interaction.followup.send(view=GWUCog.ReactionSendView(self.bot, interaction, message))
        # else:
        #     await interaction.followup.send(content="No reactions or emoji found.", ephemeral=True)
        
    async def red_delete_data_for_user(self, *, requester: RequestType, user_id: int) -> None:
        # TODO: Replace this with the proper end user data removal handling.
        super().red_delete_data_for_user(requester=requester, user_id=user_id)