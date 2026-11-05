"""Turn captured terminal output, with its ANSI colour codes, into zoetty markup."""

import re

from zoetty.markup import escape

_OSC = re.compile(r"\x1b\][^\x07\x1b]*(?:\x07|\x1b\\)")
_CSI = re.compile(r"\x1b\[([0-9;?]*)([A-Za-z])")
_COLOURS = {1: "red", 2: "green", 3: "yellow", 4: "blue", 5: "magenta", 6: "cyan"}
_ATTRIBUTES = {1: "bold", 2: "dim", 3: "italic"}


class _Pen:
    """The current text style, changed by SGR codes."""

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.bold = self.dim = self.italic = False
        self.colour: str | None = None

    def apply(self, codes: list[int]) -> None:
        index = 0
        while index < len(codes):
            code = codes[index]
            if code == 0:
                self.reset()
            elif code in _ATTRIBUTES:
                setattr(self, _ATTRIBUTES[code], True)
            elif code == 22:
                self.bold = self.dim = False
            elif code == 23:
                self.italic = False
            elif 31 <= code <= 36 or 91 <= code <= 96:
                self.colour = _COLOURS[code % 10]
            elif code in (30, 37, 39, 90, 97):
                self.colour = None
            elif code in (38, 48):
                # 256-colour (5;n) and truecolour (2;r;g;b) arguments aren't codes of their own.
                index += 2 if codes[index + 1 : index + 2] == [5] else 4
            index += 1

    def write(self, text: str) -> str:
        styles = [name for name in ("bold", "dim", "italic") if getattr(self, name)]
        if self.colour:
            styles.append(self.colour)
        text = escape(text)
        return f"[{' '.join(styles)}]{text}[/]" if styles and text.strip() else text


def to_markup(raw: str) -> list[str]:
    """One markup line per line of output, keeping colours and dropping everything else."""
    raw = _OSC.sub("", raw).replace("\r\n", "\n")
    lines = []
    for line in raw.split("\n"):
        # A carriage return moves back to the start: what's left on screen is the last thing written.
        line = line.split("\r")[-1]
        pen = _Pen()
        markup, position = "", 0
        for match in _CSI.finditer(line):
            markup += pen.write(line[position : match.start()])
            position = match.end()
            if match.group(2) == "m":
                pen.apply([int(code) for code in match.group(1).split(";") if code] or [0])
        markup += pen.write(line[position:])
        lines.append(markup.rstrip())
    while lines and not lines[-1]:
        lines.pop()
    return lines
