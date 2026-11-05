"""zoetty's markup: styled text for clip lines and prompts.

`[bold blue]text[/]` styles text, `[type 1.2]text[/]` types it out over 1.2 seconds
(`[type 1.2 0.4]` waits 0.4 seconds first), and `\\[` is a literal `[`.
"""

import re
from dataclasses import dataclass

COLOURS = ("blue", "green", "yellow", "red", "cyan", "magenta")
STYLES = ("bold", "dim", "italic", *COLOURS)
DEFAULT_TYPING_DELAY = 0.15

_TOKEN = re.compile(r"\\\[|\[(/?)([^\[\]]*)\]")


class MarkupError(ValueError):
    """Markup that can't be parsed."""


@dataclass(frozen=True)
class Segment:
    """A run of text with one set of styles, typed out if `typing` is set."""

    text: str
    styles: tuple[str, ...] = ()
    typing: float | None = None
    delay: float = DEFAULT_TYPING_DELAY


def escape(text: str) -> str:
    """Text with every `[` escaped, so it's shown exactly as it is."""
    return text.replace("[", "\\[")


def _number(value: str, markup: str) -> float:
    try:
        number = float(value)
    except ValueError:
        raise MarkupError(f"[type ...] needs numbers, got {value!r} in {markup!r}") from None
    if number < 0:
        raise MarkupError(f"[type ...] can't be negative, got {value!r} in {markup!r}")
    return number


def parse(markup: str) -> list[Segment]:
    """Split markup into styled segments. Raises MarkupError for anything it doesn't understand."""
    segments: list[Segment] = []
    styles: tuple[str, ...] = ()
    typing: float | None = None
    delay = DEFAULT_TYPING_DELAY
    text = ""
    position = 0

    def flush() -> None:
        nonlocal text
        if text:
            segments.append(Segment(text, styles, typing, delay))
            text = ""

    for match in _TOKEN.finditer(markup):
        text += markup[position : match.start()]
        position = match.end()
        if match.group(0) == "\\[":
            text += "["
            continue
        flush()
        closing, tag = match.group(1), match.group(2).split()
        if closing:
            styles, typing, delay = (), None, DEFAULT_TYPING_DELAY
        elif tag and tag[0] == "type":
            if not 2 <= len(tag) <= 3:
                raise MarkupError(f"use [type SECONDS] or [type SECONDS DELAY], got {match.group(0)!r} in {markup!r}")
            typing = _number(tag[1], markup)
            delay = _number(tag[2], markup) if len(tag) == 3 else DEFAULT_TYPING_DELAY
        else:
            unknown = [name for name in tag if name not in STYLES]
            if unknown or not tag:
                raise MarkupError(
                    f"unknown style {match.group(0)!r} in {markup!r}: styles are {', '.join(STYLES)}."
                    " Write \\[ for a literal ["
                )
            styles = tuple(tag)
    text += markup[position:]
    flush()
    return segments


def plain(segments: list[Segment]) -> str:
    """The text of some segments, without styles."""
    return "".join(segment.text for segment in segments)
