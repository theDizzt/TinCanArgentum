"""Localized help rendering for the languages with translated help content."""

import re

import fcts.i18n_runtime as i18n


ADMIN_IDS = {28, 48, 80, 82, 83, 86, 87, 88, *range(89, 100)}


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
        entry = helps.get(candidate.qualified_name) or helps.get(candidate.name)
        if entry is None:
            entry = next((data for name, data in helps.items()
                          if name != "main" and bot.get_command(name) is candidate), None)
        number = command_id(candidate, entry)
        if number is None or number in ADMIN_IDS:
            continue
        for code in ("ko", "en"):
            table = i18n.load_locale(code)
            help_key = entry.get("help_key") if entry else None
            name = table.get(
                f"{help_key}.name", table.get(f"cmd.{number:02d}.name", "")
            )
            if name.casefold() == requested.casefold():
                return candidate
    return None


def localize_listing(bot, listing, helps, language):
    if language not in {"ko", "en"}:
        return listing
    table = i18n.load_locale(language)

    def replace(match):
        name = match[1]
        entry = helps.get(name)
        if entry and entry.get("help_key"):
            display = table.get(entry["help_key"] + ".name")
            if display is not None:
                return f"`{display}`"
        number = command_id(bot.get_command(name), entry)
        if number is None or number in ADMIN_IDS:
            return match[0]
        return f"`{table.get(f'cmd.{number:02d}.name', name)}`"

    return re.sub(r"`([^`]+)`", replace, listing)


def localize_entry(command, entry, language, entry_name):
    number = command_id(command, entry)
    if language not in {"ko", "en"} or number in ADMIN_IDS:
        return entry
    if number is None and not entry.get("help_key"):
        return entry
    table = i18n.load_locale(language)
    base = f"cmd.{number:02d}" if number is not None else "cmd.00"
    result = dict(entry)
    if number is not None:
        result["id"] = f"{number:02d}"
    # Keep separate entries for commands sharing an ID (e.g. anniversary resend).
    name = entry_name
    help_base = entry.get("help_key", f"{base}.help.{name}")
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
