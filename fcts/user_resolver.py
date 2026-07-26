from __future__ import annotations

import re
import sqlite3
from contextlib import closing
from typing import Any

import discord

from config.rootdir import root_dir


MENTION_PATTERN = re.compile(r"^<@!?(\d+)>$")
TAG_PATTERN = re.compile(r"^(.+)#(\d{4})$")


class UserResolutionError(ValueError):
    pass


def _registered_users() -> list[tuple[int, str, int]]:
    with closing(sqlite3.connect(f"{root_dir}/data/user.db")) as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, nick, discrim FROM main")
        rows = cursor.fetchall()
        cursor.close()
    return [
        (int(user_id), str(nickname), int(discriminator))
        for user_id, nickname, discriminator in rows
    ]


def registered_user_tag(user_id: int | str) -> str:
    try:
        normalized_id = int(user_id)
    except (TypeError, ValueError):
        return str(user_id)

    try:
        with closing(sqlite3.connect(f"{root_dir}/data/user.db")) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT nick, discrim FROM main WHERE id = ?",
                (normalized_id,),
            )
            row = cursor.fetchone()
            cursor.close()
        if row is not None:
            return f"{row[0]}#{int(row[1]):04d}"
    except sqlite3.Error:
        pass
    return str(normalized_id)


def resolve_user_id(reference: Any) -> int:
    if hasattr(reference, "id"):
        return int(reference.id)

    value = str(reference or "").strip()
    mention = MENTION_PATTERN.fullmatch(value)
    if mention:
        return int(mention.group(1))
    if value.isdigit():
        return int(value)

    tag = TAG_PATTERN.fullmatch(value)
    if tag:
        normalized_tag = f"{tag.group(1)}#{int(tag.group(2)):04d}".casefold()
        try:
            for user_id, nickname, discriminator in _registered_users():
                candidate = f"{nickname}#{discriminator:04d}".casefold()
                if candidate == normalized_tag:
                    return user_id
        except sqlite3.Error as error:
            raise UserResolutionError("The user database could not be read.") from error

    raise UserResolutionError(
        "Use a numeric ID, a Discord member mention, or a nickname tag."
    )


async def resolve_discord_user(ctx, reference=None):
    if reference is None or not str(reference).strip():
        return ctx.author
    if isinstance(reference, (discord.Member, discord.User)):
        return reference

    user_id = resolve_user_id(reference)
    guild = getattr(ctx, "guild", None)
    if guild is not None:
        member = guild.get_member(user_id)
        if member is not None:
            return member
        try:
            return await guild.fetch_member(user_id)
        except discord.HTTPException:
            pass

    bot = ctx.bot
    user = bot.get_user(user_id)
    if user is not None:
        return user
    try:
        return await bot.fetch_user(user_id)
    except discord.HTTPException as error:
        raise UserResolutionError("The Discord user could not be found.") from error
