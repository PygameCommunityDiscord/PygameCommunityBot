"""
This file is a part of the source code for the PygameCommunityBot.
This project has been licensed under the MIT license.
Copyright (c) 2020-present pygame-community

This file defines a "routine" function, that gets called on routine.
It gets called every 5 seconds or so.
"""

import asyncio
import datetime
import io
import os
import sys

import discord
from discord.ext import tasks
import snakecore

from pgbot import common


async def handle_reminders(reminder_obj: snakecore.storage.DiscordStorage):
    """
    Handle reminder routines
    """
    new_reminders = {}
    for mem_id, reminder_dict in reminder_obj.obj.items():
        for dt, (msg, chan_id, msg_id) in reminder_dict.items():
            if datetime.datetime.utcnow() >= dt:
                content = f"__**Reminder for you:**__\n>>> {msg}"

                channel = None
                if common.guild is not None:
                    channel = common.guild.get_channel(chan_id)
                if not isinstance(channel, discord.TextChannel):
                    # Channel does not exist in the guild, DM the user
                    try:
                        user = await common.bot.fetch_user(mem_id)
                        if user.dm_channel is None:
                            await user.create_dm()

                        await user.dm_channel.send(content=content)
                    except discord.HTTPException:
                        pass
                    continue

                allowed_mentions = discord.AllowedMentions.none()
                allowed_mentions.replied_user = True
                try:
                    message = await channel.fetch_message(msg_id)
                    await message.reply(
                        content=content, allowed_mentions=allowed_mentions
                    )
                except discord.HTTPException:
                    # The message probably got deleted, try to resend in channel
                    allowed_mentions.users = [discord.Object(mem_id)]
                    content = f"__**Reminder for <@!{mem_id}>:**__\n>>> {msg}"
                    try:
                        await channel.send(
                            content=content,
                            allowed_mentions=allowed_mentions,
                        )
                    except discord.HTTPException:
                        pass
            else:
                if mem_id not in new_reminders:
                    new_reminders[mem_id] = {}

                new_reminders[mem_id][dt] = (msg, chan_id, msg_id)

    reminder_obj.obj = new_reminders


@tasks.loop(seconds=5)
async def handle_console():
    """
    Function for sending the console output to the bot-console channel.
    """
    if common.stdout is None:
        return

    contents = common.stdout.getvalue()
    # reset StringIO object for reuse
    common.stdout.truncate(0)
    common.stdout.seek(0)

    # hide path data
    contents = contents.replace(os.getcwd(), "PgBot")
    if os.name == "nt":
        contents = contents.replace(os.path.dirname(sys.executable), "Python")

    if common.GENERIC or common.console_channel is None:
        # just return if we cannot sent it on discord
        return

    # the actual message limit is 2000. But since the message is sent with
    # code ticks, we need room for those, so 1980
    for content in snakecore.utils.split_long_message(contents, 1980):
        content = content.strip()
        if not content:
            continue

        await common.console_channel.send(
            content=snakecore.utils.code_block(content, code_type="ansi")
        )


@tasks.loop(seconds=3)
async def routine():
    """
    Function that gets called routinely. This function inturn, calles other
    routine functions to handle stuff
    """
    async with snakecore.storage.DiscordStorage("reminders") as storage_obj:
        await handle_reminders(storage_obj)

    await common.bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="discord.io/pygame_community",
        )
    )
    await asyncio.sleep(3)
    await common.bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name="in discord.io/pygame_community",
        )
    )
