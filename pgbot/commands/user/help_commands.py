"""
This file is a part of the source code for the PygameCommunityBot.
This project has been licensed under the MIT license.
Copyright (c) 2020-present PygameCommunityDiscord

This file defines the command handler class for the "help" commands of the bot
"""

from __future__ import annotations

import os
import random
import re
import time
from typing import Optional

import discord
from discord.ext import commands
import pygame
import snakecore
from snakecore.command_handler.decorators import custom_parsing

import pgbot
from pgbot import common, db
from pgbot.commands.base import BaseCommandCog
from pgbot.commands.utils import clock, docs, help
from pgbot.commands.utils.converters import String
from pgbot.exceptions import BotException


class HelpCommandCog(BaseCommandCog):
    """Base commang cog to handle 'help' commands of the bot."""

    @commands.command()
    @custom_parsing(inside_class=True, inject_message_reference=True)
    async def rules(self, ctx: commands.Context, *rules: int):
        """
        ->type Get help
        ->signature pg!rules [*rule_numbers]
        ->description Get rules of the server
        -----
        Implement pg!rules, to get rules of the server
        """

        response_message = common.recent_response_messages[ctx.message.id]

        if not rules:
            raise BotException("Please enter rule number(s)", "")

        if common.GENERIC:
            raise BotException(
                "Cannot execute command!",
                "This command cannot be exected when the bot is on generic mode",
            )

        fields = []
        for rule in sorted(set(rules)):
            if 0 < rule <= len(common.ServerConstants.RULES):
                msg = await common.rules_channel.fetch_message(
                    common.ServerConstants.RULES[rule - 1]
                )
                value = msg.content

            elif rule == 42:
                value = (
                    "*Shhhhh*, you have found an unwritten rule!\n"
                    "Click [here](https://bitly.com/98K8eH) to gain the most "
                    "secret and ultimate info!"
                )

            else:
                value = "Does not exist lol"

            if len(str(rule)) > 200:
                raise BotException(
                    "Overflow in command",
                    "Why would you want to check such a large rule number?",
                )

            fields.append(
                {
                    "name": f"__Rule number {rule}:__",
                    "value": value,
                    "inline": False,
                }
            )

        if len(rules) > 25:
            raise BotException(
                "Overflow in command",
                "Too many rules were requested",
            )

        if len(rules) == 1:
            await snakecore.utils.embed_utils.replace_embed_at(
                response_message,
                author_name="Pygame Community",
                author_icon_url=common.GUILD_ICON,
                title=fields[0]["name"],
                description=fields[0]["value"][:2048],
                color=0x228B22,
            )
        else:
            for field in fields:
                field["value"] = field["value"][:1024]

            await snakecore.utils.embed_utils.replace_embed_at(
                response_message,
                author_name="Pygame Community",
                author_icon_url=common.GUILD_ICON,
                title="Rules",
                fields=fields,
                color=0x228B22,
            )

    async def clock_func(
        self,
        ctx: commands.Context,
        action: str = "",
        timezone: Optional[float] = None,
        color: Optional[discord.Color] = None,
        _member: Optional[discord.Member] = None,
    ):

        response_message = common.recent_response_messages[ctx.message.id]

        async with db.DiscordDB("clock") as db_obj:
            timezones = db_obj.get({})
            if action:
                if _member is None:
                    member = ctx.author
                    if member.id not in timezones:
                        raise BotException(
                            "Cannot update clock!",
                            "You cannot run clock update commands because you are "
                            + "not on the clock",
                        )
                else:
                    member = _member

                if action == "update":
                    if timezone is not None and abs(timezone) > 12:
                        raise BotException(
                            "Failed to update clock!", "Timezone offset out of range"
                        )

                    if member.id in timezones:
                        if timezone is not None:
                            timezones[member.id][0] = timezone
                        if color is not None:
                            timezones[member.id][1] = pgbot.utils.color_to_rgb_int(
                                color
                            )
                    else:
                        if timezone is None:
                            raise BotException(
                                "Failed to update clock!",
                                "Timezone is required when adding new people",
                            )

                        if color is None:
                            color = discord.Color(random.randint(0, 0xFFFFFF))

                        timezones[member.id] = [
                            timezone,
                            color.value,
                        ]

                    # sort timezones dict after an update operation
                    timezones = dict(sorted(timezones.items(), key=lambda x: x[1][0]))

                elif action == "remove":
                    try:
                        timezones.pop(member.id)
                    except KeyError:
                        raise BotException(
                            "Failed to update clock!",
                            "Cannot remove non-existing person from clock",
                        )

                else:
                    raise BotException(
                        "Failed to update clock!", f"Invalid action specifier {action}"
                    )

                db_obj.write(timezones)

        t = time.time()

        pygame.image.save(
            await clock.user_clock(t, timezones, ctx.guild), f"temp{t}.png"
        )
        await response_message.edit(
            embeds=[], attachments=[discord.File(f"temp{t}.png")]
        )
        os.remove(f"temp{t}.png")

    @commands.command()
    @custom_parsing(inside_class=True, inject_message_reference=True)
    async def clock(
        self,
        ctx: commands.Context,
        action: str = "",
        timezone: Optional[float] = None,
        color: Optional[discord.Color] = None,
    ):
        """
        ->type Get help
        ->signature pg!clock
        ->description 24 Hour Clock showing <@&778205389942030377> s who are available to help
        -> Extended description
        People on the clock can run the clock with more arguments, to update their data.
        `pg!clock update [timezone in hours] [color as hex string]`
        `timezone` is float offset from GMT in hours.
        `color` optional color argument, that shows up on the clock.
        Note that you might not always display with that colour.
        This happens if more than one person are on the same timezone
        Use `pg!clock remove` to remove yourself from the clock
        -----
        Implement pg!clock, to display a clock of helpfulies/mods/wizards
        """

        return await self.clock_func(ctx, action=action, timezone=timezone, color=color)

    @commands.command()
    @custom_parsing(inside_class=True, inject_message_reference=True)
    async def doc(
        self,
        ctx: commands.Context,
        name: str,
        page: int = 1,
    ):
        """
        ->type Get help
        ->signature pg!doc <object name>
        ->description Look up the docstring of a Python/Pygame object, e.g str or pygame.Rect
        -----
        Implement pg!doc, to view documentation
        """

        # needed for typecheckers to know that ctx.author is a member
        if isinstance(ctx.author, discord.User):
            return

        response_message = common.recent_response_messages[ctx.message.id]

        await docs.put_doc(ctx, name, response_message, ctx.author, page=page)

    @commands.command()
    @custom_parsing(inside_class=True, inject_message_reference=True)
    async def help(
        self,
        ctx: commands.Context,
        *names: str,
        page: int = 1,
    ):
        """
        ->type Get help
        ->signature pg!help [command]
        ->description Ask me for help
        ->example command pg!help help
        -----
        Implement pg!help, to display a help message
        """

        # needed for typecheckers to know that ctx.author is a member
        if isinstance(ctx.author, discord.User):
            return

        response_message = common.recent_response_messages[ctx.message.id]

        await help.send_help_message(
            ctx,
            response_message,
            ctx.author,
            names,
            self.cmds_and_funcs,
            self.groups,
            page=page,
        )

    @commands.command()
    @custom_parsing(inside_class=True, inject_message_reference=True)
    async def resources(
        self,
        ctx: commands.Context,
        limit: Optional[int] = None,
        filter_tag: Optional[String] = None,
        filter_members: Optional[tuple[discord.Object, ...]] = None,
        oldest_first: bool = False,
        page: int = 1,
    ):
        """
        ->type Get help
        ->signature pg!resources [limit] [filter_tag] [filter_members] [oldest_first]
        ->description Browse through resources.
        ->extended description
        pg!resources takes in additional arguments, though they are optional.
        `oldest_first`: Set oldest_first to True to browse through the oldest resources
        `limit=[num]`: Limits the number of resources to the number
        `filter_tag=[tag]`: Includes only the resources with that tag(s)
        `filter_members=[members]`: Includes only the resources posted by those user(s). Can be a tuple of users
        ->example command pg!resources limit=5 oldest_first=True filter_tag="python, gamedev" filter_member=444116866944991236
        """

        # needed for typecheckers to know that ctx.author is a member
        if isinstance(ctx.author, discord.User):
            return

        response_message = common.recent_response_messages[ctx.message.id]

        if common.GENERIC:
            raise BotException(
                "Cannot execute command!",
                "This command cannot be exected when the bot is on generic mode",
            )

        def process_tag(tag: str):
            for to_replace in ("tag_", "tag-", "<", ">", "`"):
                tag = tag.replace(to_replace, "")
            return tag.title()

        resource_entries_channel = common.entry_channels["resource"]

        # Retrieves all messages inside resource entries channel
        msgs: list[discord.Message] = []
        async for msg in resource_entries_channel.history(oldest_first=oldest_first):
            if msg.id not in common.ServerConstants.MSGS_TO_FILTER:
                msgs.append(msg)

        if filter_tag:
            # Filter messages based on tag
            for tag in map(str.strip, filter_tag.string.split(",")):
                tag = tag.lower()
                msgs = list(
                    filter(
                        lambda x: f"tag_{tag}" in x.content.lower()
                        or f"tag-<{tag}>" in x.content.lower(),
                        msgs,
                    )
                )

        if filter_members:
            filter_member_ids = [obj.id for obj in filter_members]
            msgs = list(filter(lambda x: x.author.id in filter_member_ids, msgs))

        if limit is not None:
            # Uses list slicing instead of TextChannel.history's limit param
            # to include all param specified messages
            msgs = msgs[:limit]

        tags = {}
        old_tags = {}
        links = {}
        for msg in msgs:
            # Stores the tags (tag_{Your tag here}), old tags (tag-<{your tag here}>),
            # And links inside separate dicts with regex
            links[msg.id] = [
                match.group()
                for match in re.finditer("http[s]?://(www.)?[^ \n]+", msg.content)
            ]
            tags[msg.id] = [
                f"`{process_tag(match.group())}` "
                for match in re.finditer("tag_.+", msg.content.lower())
            ]
            old_tags[msg.id] = [
                f"`{process_tag(match.group())}` "
                for match in re.finditer("tag-<.+>", msg.content.lower())
            ]

        pages = []
        copy_msgs = msgs[:]
        i = 1
        while msgs:
            # Constructs embeds based on messages, and store them in pages to
            # be used in the paginator
            top_msg = msgs[:6]
            if len(copy_msgs) > 1:
                title = (
                    f"Retrieved {len(copy_msgs)} entries in "
                    f"#{resource_entries_channel.name}"
                )
            else:
                title = (
                    f"Retrieved {len(copy_msgs)} entry in "
                    f"#{resource_entries_channel.name}"
                )
            current_embed = discord.Embed(title=title)

            # Cycles through the top 6 messages
            for msg in top_msg:
                try:
                    name = msg.content.split("\n")[1].strip().replace("**", "")
                    if not name:
                        continue

                    field_name = f"{i}. {name}, posted by {msg.author.display_name}"
                    # If the field name is > 256 (discord limit), shorten it
                    # with list slicing
                    field_name = f"{field_name[:253]}..."

                    value = msg.content.split(name)[1].removeprefix("**").strip()
                    # If the preview of the resources > 80, shorten it with list slicing
                    value = f"{value[:80]}..."
                    value += f"\n\nLinks: **[Message]({msg.jump_url})**"

                    for j, link in enumerate(links[msg.id], 1):
                        value += f", [Link {j}]({link})"

                    value += "\nTags: "
                    if tags[msg.id]:
                        value += "".join(tags[msg.id]).removesuffix(",")
                    elif old_tags[msg.id]:
                        value += "".join(old_tags[msg.id]).removesuffix(",")
                    else:
                        value += "None"

                    current_embed.add_field(
                        name=field_name,
                        value=f"{value}\n{common.ZERO_SPACE}",
                        inline=True,
                    )
                    i += 1
                except IndexError:
                    # Suppresses IndexError because of rare bug
                    pass

            pages.append(current_embed)
            msgs = msgs[6:]

        if not pages:
            raise BotException(
                f"Retrieved 0 entries in #{resource_entries_channel.name}",
                "There are no results of resources with those parameters. "
                "Please try again.",
            )

        footer_text = (
            "Refresh this by replying with "
            f"`{common.COMMAND_PREFIX}refresh`.\ncmd: resources"
        )

        raw_command_input: str = getattr(ctx, "raw_command_input", "")
        # attribute injected by snakecore's custom parser

        if raw_command_input:
            footer_text += f" | args: {raw_command_input}"

        msg_embeds = [
            snakecore.utils.embed_utils.create_embed(
                color=common.DEFAULT_EMBED_COLOR, footer_text=footer_text
            )
        ]

        target_message = await response_message.edit(embeds=msg_embeds)

        # Creates a paginator for the caller to use
        paginator = snakecore.utils.pagination.EmbedPaginator(
            target_message,
            *pages,
            caller=ctx.author,
            whitelisted_role_ids=common.ServerConstants.ADMIN_ROLES,
            start_page_number=page,
            inactivity_timeout=60,
            theme_color=common.DEFAULT_EMBED_COLOR,
        )

        try:
            await paginator.mainloop()
        except discord.HTTPException:
            pass
