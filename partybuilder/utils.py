import re
import discord
import emoji

from redbot.core import commands
from redbot.core.utils import bounded_gather
from typing import Union, List, Dict

DiscordEmoji = Union[discord.PartialEmoji, discord.Emoji, str]
emoji_regex = re.compile(r'<(a?):([A-Za-z0-9_]{2,32}):(\d+)>')

async def gather_reactions(message: discord.Message) -> Dict[Union[discord.PartialEmoji, discord.Emoji, str], List[Union[discord.Member, discord.User]]]:
    react_data = {}
    for r in message.reactions:
        mentions = [u async for u in r.users() if not u.bot]
        if mentions:
            react_data[r.emoji] = mentions

    return react_data

def get_emoji_name(e:DiscordEmoji, lang:str):
    code = lang[:2]
    if code not in emoji.LANGUAGES:
        code = 'alias'

    if type(e) is discord.Emoji:
        return e.name
    elif type(e) is discord.PartialEmoji:
        return e.name
    elif type(e) is str:
        return emoji.demojize(e, language=code, delimiters=("", ""))
    else: 
        return None
    

def get_emojis_from_text(bot:commands.Bot, text:str):
    used_emoji = [(m.start(), bot.get_emoji(int(m.group(3)))) for m in emoji_regex.finditer(text)]
    used_standard_emoji = [(e['match_start'], e['emoji']) for e in emoji.emoji_list(text)]
    seen = set()
    for i, e in sorted(used_emoji + used_standard_emoji):
        if e and e not in seen:
            seen.add(e)
            yield e

def clamp_with_ellipsis(text: str, max_length: int) -> str:
    return text if len(text) <= max_length else text[:max_length - 1] + "…"

def generate_default_thread_name(message: discord.Message, default: str) -> str:
    # Include alt text from the first attachment (if any)
    if message.attachments:
        description = message.attachments[0].description
        if description and len(description) > 0:
            return clamp_with_ellipsis(description, 40)

    # Use the title from the first embed (if any)
    if message.embeds:
        title = message.embeds[0].title
        if title and len(title) > 0:
            return clamp_with_ellipsis(title, 40)

    # Fallback to message content
    words = re.split(r"\s+", message.content)
    output = ""
    for word in words:
        # Little different to default discord algorithm,
        # strip custom emoji as they aren't shown in thread titles.
        if not re.match(r'<:\w*:\d*>', word):
            if len(output) + len(word) > 41:
                break
            output += word + " "

    output = output.strip()

    if words and len(output) == 0:
        output = clamp_with_ellipsis(words[0], 40)

    if len(output) == 0:
        output = default

    return clamp_with_ellipsis(output, 41)