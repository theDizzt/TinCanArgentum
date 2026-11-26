"""Localized help rendering for the languages with translated help content."""

import re

import fcts.i18n_runtime as i18n


ADMIN_IDS = {28, 82, 83, 87, 88, *range(89, 100)}


def command_id(command, entry=None):
    app_command = getattr(command, "app_command", None)
    locale_name = getattr(app_command, "_locale_name", None)
    key = getattr(locale_name, "extras", {}).get("key", "")
    match = re.fullmatch(r"cmd\.(\d+)\.name", key)
    if match:
        return int(match[1])
    if entry and str(entry.get("id", "")).isdigit():
        return int(entry["id"])
    return None


def resolve_command(bot, requested, helps, language):
    command = bot.get_command(requested)
    if command is not None or language not in {"ko", "en"}:
        return command
    for candidate in bot.walk_commands():
        number = command_id(candidate, helps.get(candidate.name))
        if number is None or number in ADMIN_IDS:
            continue
        for code in ("ko", "en"):
            name = i18n.load_locale(code).get(f"cmd.{number:02d}.name", "")
            if name.casefold() == requested.casefold():
                return candidate
    return None


def localize_listing(bot, listing, helps, language):
    if language not in {"ko", "en"}:
        return listing
    table = i18n.load_locale(language)

    def replace(match):
        name = match[1]
        number = command_id(bot.get_command(name), helps.get(name))
        if number is None or number in ADMIN_IDS:
            return match[0]
        return f"`{table.get(f'cmd.{number:02d}.name', name)}`"

    return re.sub(r"`([^`]+)`", replace, listing)


def localize_entry(command, entry, language, entry_name):
    number = command_id(command, entry)
    if language not in {"ko", "en"} or number is None or number in ADMIN_IDS:
        return entry
    table = i18n.load_locale(language)
    base = f"cmd.{number:02d}"
    result = dict(entry)
    result["id"] = f"{number:02d}"
    # Keep separate entries for commands sharing an ID (e.g. anniversary resend).
    name = entry_name
    help_base = f"{base}.help.{name}"
    result["title"] = table.get(
        f"{help_base}.title", table.get(f"{base}.name", entry["title"])
    )
    for field in ("ctx", "discript", "args"):
        result[field] = table.get(f"{help_base}.{field}", result[field])
    result["discript"] = table.get(
        f"{help_base}.discript", table.get(f"{base}.desc", result["discript"])
    )
    syntax = result["ctx"].split(maxsplit=1)
    if syntax and f"{help_base}.ctx" not in table:
        result["ctx"] = result["title"] + (f" {syntax[1]}" if len(syntax) > 1 else "")
    return result
