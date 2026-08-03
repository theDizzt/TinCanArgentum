"""Parser for LINE plain-text group-chat exports."""

from dataclasses import dataclass
import re
from typing import Iterable


MESSAGE_PATTERN = re.compile(
    r"^(?P<time>(?:[01]\d|2[0-3]):[0-5]\d)\s+"
    r"(?P<name>\S{2})\s+(?P<content>.*)$"
)
TIME_PREFIX_PATTERN = re.compile(r"^(?:[01]\d|2[0-3]):[0-5]\d(?:\s|$)")
DATE_PATTERN = re.compile(r"^\d{4}\.\d{1,2}\.\d{1,2}(?:\s+.*)?$")


@dataclass(frozen=True)
class LineMessage:
    time: str
    name: str
    content: str


def parse_line_messages(lines: Iterable[str]) -> list[LineMessage]:
    """Parse LINE rows, joining continuation lines into their parent message."""
    messages = []
    current = None

    def finish_current():
        nonlocal current
        if current is not None:
            messages.append(
                LineMessage(
                    time=current["time"],
                    name=current["name"],
                    content="\n".join(current["content"]),
                )
            )
            current = None

    for raw_line in lines:
        line = raw_line.rstrip("\r\n")

        if DATE_PATTERN.fullmatch(line.strip()):
            finish_current()
            continue

        match = MESSAGE_PATTERN.fullmatch(line)
        if match is not None:
            finish_current()
            current = {
                "time": match.group("time"),
                "name": match.group("name"),
                "content": [match.group("content")],
            }
            continue

        # A timestamp with an invalid speaker shape is a separate unsupported
        # record, not a continuation of the previous user's message.
        if TIME_PREFIX_PATTERN.match(line):
            finish_current()
            continue

        if current is not None and line:
            current["content"].append(line)

    finish_current()
    return messages


def read_line_export(path) -> list[LineMessage]:
    """Read a UTF-8 LINE export and return its parsed messages."""
    with path.open(encoding="utf-8-sig") as export_file:
        return parse_line_messages(export_file)
