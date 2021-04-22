import asyncio
import datetime as dt
import re
from datetime import datetime
import discord
from discord.embeds import EmptyEmbed

from . import common

class ArgError(Exception):
    pass

def format_time(seconds: float, decimal_places: int = 4):
    """
    Formats time with a prefix
    """
    for fractions, unit in (
        (1.0, "s"),
        (1e-03, "ms"),
        (1e-06, "\u03bcs"),
        (1e-09, "ns"),
        (1e-12, "ps"),
        (1e-15, "fs"),
        (1e-18, "as"),
        (1e-21, "zs"),
        (1e-24, "ys"),
    ):
        if seconds >= fractions:
            return f"{seconds / fractions:.0{decimal_places}f} {unit}"
    return f"very fast"


def format_long_time(seconds):
    result = []

    for name, count in (
            ('weeks', 604800),
            ('days', 86400),
            ('hours', 3600),
            ('minutes', 60),
            ('seconds', 1),
    ):
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name[:-1]
            result.append("{} {}".format(value, name))
    return ', '.join(result)


def format_byte(size: int, decimal_places=3):
    """
    Formats a given size and outputs a string equivalent to B, KB, MB, or GB
    """
    if size < 1e03:
        return f"{round(size, decimal_places)} B"
    if size < 1e06:
        return f"{round(size / 1e3, decimal_places)} KB"
    if size < 1e09:
        return f"{round(size / 1e6, decimal_places)} MB"

    return f"{round(size / 1e9, decimal_places)} GB"


def split_long_message(message: str):
    """
    Splits message string by 2000 characters with safe newline splitting
    """
    split_output = []
    lines = message.split('\n')
    temp = ""

    for line in lines:
        if len(temp) + len(line) + 1 > 2000:
            split_output.append(temp[:-1])
            temp = line + '\n'
        else:
            temp += line + '\n'

    if temp:
        split_output.append(temp)

    return split_output


def filter_id(mention: str):
    """
    Filters mention to get ID "<@!6969>" to "6969"
    Note that this function can error with ValueError on the int call, so the
    caller of this function must take care of this
    """
    for char in ("<", ">", "@", "&", "#", "!", " "):
        mention = mention.replace(char, "")

    return int(mention)


def get_embed_fields(messages):
    # syntax: <Field|Title|desc.[|inline=False]>
    field_regex = r"(<.*\|.*(\|True|\|False|)>)"
    field_datas = []

    for message in messages:
        field_list = re.split(field_regex, message)
        for field in field_list:
            if field:
                field = field.lstrip().rstrip()[1:-1]  #remove < and >
                field_data = field.split("|")

                if len(field_data) not in (2, 3):
                    continue
                elif len(field_data) == 2:
                    field_data.append("")

                field_data[2] = True if field_data[2] == "True" else False

                field_datas.append(field_data)

    return field_datas


async def edit_embed(message, title, description, color=0xFFFFAA, url_image=None, fields=[]):
    """
    Edits the embed of a message with a much more tight function
    """
    embed = discord.Embed(title=title, description=description, color=color)
    if url_image:
        embed.set_image(url=url_image)

    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    return await message.edit(embed=embed)


async def send_embed(channel, title, description, color=0xFFFFAA, url_image=None, fields=[]):
    """
    Sends an embed with a much more tight function
    """
    embed = discord.Embed(title=title, description=description, color=color)
    if url_image:
        embed.set_image(url=url_image)

    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    return await channel.send(embed=embed)


async def send_embed_2(
    channel, embed_type="rich", author_name=EmptyEmbed, author_url=EmptyEmbed, author_icon_url=EmptyEmbed, title=EmptyEmbed, url=EmptyEmbed, thumbnail_url=EmptyEmbed,
    description=EmptyEmbed, image_url=EmptyEmbed, color=0xFFFFAA, fields=[], footer_text=EmptyEmbed, footer_icon_url=EmptyEmbed, timestamp=EmptyEmbed
):
    """
    Sends an embed with a much more tight function
    """

    embed = discord.Embed(title=title, type=embed_type,
                          url=url, description=description, color=color)

    if timestamp:
        if isinstance(timestamp, str):
            embed.timestamp = datetime.fromisoformat(timestamp)
        else:
            embed.timestamp = timestamp

    if author_name:
        embed.set_author(name=author_name, url=author_url,
                         icon_url=author_icon_url)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    if image_url:
        embed.set_image(url=image_url)

    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    embed.set_footer(text=footer_text, icon_url=footer_icon_url)

    return await channel.send(embed=embed)


async def edit_embed_2(
    message, embed_type="rich", author_name=EmptyEmbed, author_url=EmptyEmbed, author_icon_url=EmptyEmbed, title=EmptyEmbed, url=EmptyEmbed, thumbnail_url=EmptyEmbed,
    description=EmptyEmbed, image_url=EmptyEmbed, color=0xFFFFAA, fields=[], footer_text=EmptyEmbed, footer_icon_url=EmptyEmbed, timestamp=EmptyEmbed
):
    """
    Edits the embed of a message with a much more tight function
    """

    embed = discord.Embed(title=title, type=embed_type,
                          url=url, description=description, color=color)

    if timestamp:
        if isinstance(timestamp, str):
            embed.timestamp = datetime.fromisoformat(timestamp)
        else:
            embed.timestamp = timestamp

    if author_name:
        embed.set_author(name=author_name, url=author_url,
                         icon_url=author_icon_url)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    if image_url:
        embed.set_image(url=image_url)

    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    embed.set_footer(text=footer_text, icon_url=footer_icon_url)

    return await message.edit(embed=embed)

async def update_embed_2(
    message, embed, embed_type="rich", author_name=EmptyEmbed, author_url=EmptyEmbed, author_icon_url=EmptyEmbed, title=EmptyEmbed, url=EmptyEmbed, thumbnail_url=EmptyEmbed,
    description=EmptyEmbed, image_url=EmptyEmbed, color=0xFFFFAA, fields=[], footer_text=EmptyEmbed, footer_icon_url=EmptyEmbed, timestamp=EmptyEmbed
):
    """
    Updates the changed attributes of the embed of a message with a much more tight function
    """

    update_embed = discord.Embed(
        title=title, type=embed_type, url=url, description=description, color=color
    )

    if timestamp:
        if isinstance(timestamp, str):
            embed.timestamp = datetime.fromisoformat(timestamp)
        else:
            embed.timestamp = timestamp

    if author_name:
        embed.set_author(name=author_name, url=author_url,
                         icon_url=author_icon_url)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    if image_url:
        embed.set_image(url=image_url)

    for field in fields:
        embed.add_field(name=field[0], value=field[1], inline=field[2])

    embed.set_footer(text=footer_text, icon_url=footer_icon_url)

    old_embed_dict = embed.to_dict()
    update_embed_dict = update_embed.to_dict()

    if "author" in old_embed_dict and "author" in update_embed_dict:
        old_embed_dict["author"].update(update_embed_dict["author"])
    
    if "footer" in old_embed_dict and "footer" in update_embed_dict:
        old_embed_dict["footer"].update(update_embed_dict["footer"])
        
    old_embed_dict.update(update_embed_dict)

    return await message.edit(embed=discord.Embed.from_dict(old_embed_dict))


async def send_embed_from_dict(channel, data):
    """
    Sends an embed from a dictionary with a much more tight function
    """
    return await channel.send(embed=discord.Embed.from_dict(data))


async def edit_embed_from_dict(message, data):
    """
    Edits the embed of a message from a dictionary with a much more tight 
    function
    """
    return await message.edit(embed=discord.Embed.from_dict(data))


async def update_embed_from_dict(message, embed, data):
    """
    Updates the changed attributes of the embed of a message from a dictionary with a much more tight function
    """
    old_embed_dict = embed.to_dict()
    update_embed_dict = data

    if "author" in old_embed_dict and update_embed_dict:
        old_embed_dict["author"].update(update_embed_dict["author"])
    
    if "footer" in old_embed_dict and update_embed_dict:
        old_embed_dict["footer"].update(update_embed_dict["footer"])
        
    old_embed_dict.update(update_embed_dict)

    return await message.edit(embed=discord.Embed.from_dict(old_embed_dict))


async def update_embed_field_from_dict(message, embed, field_dict, index):
    """
    Updates an embed field of the embed of a message from a dictionary with a much more tight function
    """
    
    if "name" in field_dict and "value" in field_dict and "inline" in field_dict:
        embed.set_field_at(index, name=field_dict["name"], value=field_dict["value"], inline=field_dict["inline"])

    return await message.edit(embed=embed)

async def add_embed_field_from_dict(message, embed, field_dict):
    """
    Adds an embed field to the embed of a message from a dictionary with a much more tight function
    """
    
    if "name" in field_dict and "value" in field_dict and "inline" in field_dict:
        embed.add_field(name=field_dict["name"], value=field_dict["value"], inline=field_dict["inline"])

    return await message.edit(embed=embed)

async def insert_embed_field_from_dict(message, embed, field_dict, index):
    """
    Inserts an embed field of the embed of a message from a dictionary with a much more tight function
    """
    
    if "name" in field_dict and "value" in field_dict and "inline" in field_dict:
        embed.insert_field_at(index, name=field_dict["name"], value=field_dict["value"], inline=field_dict["inline"])

    return await message.edit(embed=embed)



def format_entries_message(message, entry_type):
    title = f"New {entry_type.lower()} in #{common.ZERO_SPACE}{common.entry_channels[entry_type].name}"
    fields = []

    msg_link = "[View](https://discordapp.com/channels/" \
        f"{message.author.guild.id}/{message.channel.id}/{message.id})"

    attachments = ""
    if message.attachments:
        for i, attachment in enumerate(message.attachments):
            attachments += f" • [Link {i+1}]({attachment.url})\n"
    else:
        attachments = "No attachments"

    msg = message.content if message.content else "No description provided."

    fields.append(["**Posted by**", message.author.mention, True])
    fields.append(["**Original msg.**", msg_link, True])
    fields.append(["**Attachments**", attachments, True])
    fields.append(["**Description**", msg, True])

    return title, fields


async def format_archive_messages(messages):
    """
    Formats a message to be archived
    """
    formatted_msgs = []
    for message in messages:
        triple_block_quote = '```'

        author = f"{message.author} ({message.author.mention}) [{message.author.id}]"
        content = message.content.replace(
            '\n', '\n> ') if message.content else None

        if message.attachments:
            attachment_list = []
            for i, attachment in enumerate(message.attachments, 1):
                filename = repr(attachment.filename)
                attachment_list.append(
                    f'{i}:\n    **Name**: {filename}\n    **URL**: {attachment.url}')
            attachments = '\n> '.join(attachment_list)
        else:
            attachments = ""

        if message.embeds:
            embed_list = []
            for i, embed in enumerate(message.embeds, 1):
                if isinstance(embed, discord.Embed):
                    if isinstance(embed.description, str):
                        desc = embed.description.replace(
                            triple_block_quote, common.ESC_BACKTICK_3X)
                    else:
                        desc = '\n'

                    embed_list.append(
                        f'{i}:\n\t**Title**: {embed.title}\n\t**Description**: ```\n{desc}```\n\t**Image URL**: {embed.image.url}')
                else:
                    embed_list.append('\n')
            embeds = '\n> '.join(embed_list)
        else:
            embeds = ""

        formatted_msgs.append(
            f"**AUTHOR**: {author}\n"
            + (f"**MESSAGE**: \n> {content}\n" if content else "")
            + (f"**ATTACHMENT(S)**: \n> {attachments}\n" if message.attachments else "")
            + (f"**EMBED(S)**: \n> {embeds}\n" if message.embeds else "")
        )
        await asyncio.sleep(0.01)  # Lets the bot do other things

    return formatted_msgs


def code_block(string: str, max_characters=2048):
    """
    Formats text into discord code blocks
    """
    string = string.replace("```", "\u200b`\u200b`\u200b`\u200b")
    max_characters -= 7

    if len(string) > max_characters:
        return f"```\n{string[:max_characters - 7]} ...```"
    else:
        return f"```\n{string[:max_characters]}```"
