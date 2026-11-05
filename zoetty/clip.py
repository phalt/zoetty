"""Load and validate clip spec files (TOML)."""

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from zoetty.markup import COLOURS, MarkupError, parse

DEFAULT_PROMPT = "[dim]$[/] "

THEME = {
    "bg": "#1c1c1c",
    "fg": "#d0d0d0",
    "bar": "#2a2a2a",
    "blue": "#4b8fe3",
    "green": "#2fcf7a",
    "yellow": "#e6e04a",
    "red": "#e05252",
    "cyan": "#4fc6d6",
    "magenta": "#c678dd",
}
assert set(THEME) == {"bg", "fg", "bar", *COLOURS}

FORMATS = (".svg", ".html")
_HEX = re.compile(r"#[0-9a-fA-F]{3}(?:[0-9a-fA-F]{3})?")


class ClipError(Exception):
    """A spec file that can't be used, with every problem found in it."""

    def __init__(self, path: Path, problems: list[str]) -> None:
        self.path = path
        self.problems = problems
        super().__init__(f"{path}: " + "; ".join(problems))


@dataclass(frozen=True)
class Record:
    """How `zoetty record` runs a clip's commands."""

    cwd: Path
    setup: list[str] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    timeout: float = 60


@dataclass(frozen=True)
class Run:
    """A command typed at the prompt, and what it printed."""

    cmd: str
    exec: str | None = None
    output: Path | None = None
    lines: list[str] | None = None
    input: str | None = None
    record: bool = True
    prompt: str | None = None
    think: float = 0.5
    pause: float = 0.9
    line_gap: float | None = None

    @property
    def command(self) -> str:
        """What `record` actually runs."""
        return self.exec or self.cmd

    @property
    def recordable(self) -> bool:
        return self.output is not None and self.record


@dataclass(frozen=True)
class Step:
    """Lines that appear together at a set time, for clips that aren't command sessions."""

    at: float
    lines: list[str]
    caret: bool = False


@dataclass(frozen=True)
class Clip:
    path: Path
    label: str
    out: list[Path]
    record: Record
    theme: dict[str, str]
    title: str = ""
    cols: int = 80
    rows: int | None = None
    prompt: str = DEFAULT_PROMPT
    final_prompt: str | None = None
    typing_speed: float = 28
    line_gap: float = 0.07
    hold: float = 4.0
    duration: float | None = None
    chrome: bool = True
    runs: list[Run] = field(default_factory=list)
    steps: list[Step] = field(default_factory=list)


# Each key's type and check. `number` allows ints and floats, never bools.
_Kind = str
_TOP = {
    "title": "str",
    "label": "str",
    "cols": "positive int",
    "rows": "positive int",
    "out": "list of str",
    "prompt": "markup",
    "final_prompt": "markup",
    "typing_speed": "positive number",
    "line_gap": "number",
    "hold": "number",
    "duration": "positive number",
    "chrome": "bool",
    "record": "table",
    "theme": "table",
    "run": "list of tables",
    "step": "list of tables",
}
_RECORD = {"cwd": "str", "setup": "list of str", "env": "table of str", "timeout": "positive number"}
_RUN = {
    "cmd": "str",
    "exec": "str",
    "output": "str",
    "lines": "list of markup",
    "input": "str",
    "record": "bool",
    "prompt": "markup",
    "think": "number",
    "pause": "number",
    "line_gap": "number",
}
_STEP = {"at": "number", "lines": "list of markup", "caret": "bool"}


def _number(value: Any) -> bool:
    return isinstance(value, int | float) and not isinstance(value, bool)


def _problem(kind: _Kind, value: Any) -> str | None:
    """Why a value isn't of a kind, or None if it is."""
    match kind:
        case "str":
            ok = isinstance(value, str)
        case "bool":
            ok = isinstance(value, bool)
        case "positive int":
            ok = isinstance(value, int) and not isinstance(value, bool) and value > 0
        case "number":
            ok = _number(value) and value >= 0
            kind = "number, 0 or more"
        case "positive number":
            ok = _number(value) and value > 0
        case "table":
            ok = isinstance(value, dict)
        case "table of str":
            ok = isinstance(value, dict) and all(isinstance(item, str) for item in value.values())
        case "list of tables":
            ok = isinstance(value, list) and all(isinstance(item, dict) for item in value)
        case "markup" | "list of markup" | "list of str":
            items = [value] if kind == "markup" else value
            ok = (kind == "markup" or isinstance(value, list)) and all(isinstance(item, str) for item in items)
            if ok and kind != "list of str":
                for item in items:
                    try:
                        parse(item)
                    except MarkupError as error:
                        return str(error)
        case _:  # pragma: no cover
            raise AssertionError(kind)
    return None if ok else f"should be a {kind}, got {value!r}"


def _check(table: dict[str, Any], keys: dict[str, _Kind], where: str, problems: list[str]) -> None:
    for key, value in table.items():
        if key not in keys:
            problems.append(f"{where}unknown key {key!r}")
        elif problem := _problem(keys[key], value):
            problems.append(f"{where}{key} {problem}")


def load(path: Path) -> Clip:
    """Read a spec file. Raises ClipError listing every problem in it."""
    try:
        data = tomllib.loads(path.read_text())
    except OSError as error:
        raise ClipError(path, [f"can't read it: {error.strerror}"]) from None
    except tomllib.TOMLDecodeError as error:
        raise ClipError(path, [f"isn't valid TOML: {error}"]) from None

    problems: list[str] = []
    _check(data, _TOP, "", problems)
    if "label" not in data:
        problems.append("label is required: it's the alt text people without the animation get")
    record = data.get("record", {}) if isinstance(data.get("record"), dict) else {}
    _check(record, _RECORD, "record.", problems)
    theme = data.get("theme", {}) if isinstance(data.get("theme"), dict) else {}
    for key, value in theme.items():
        if key not in THEME:
            problems.append(f"theme.{key} isn't a theme colour: use {', '.join(THEME)}")
        elif not isinstance(value, str) or not _HEX.fullmatch(value):
            problems.append(f"theme.{key} should be a colour like '#282c34', got {value!r}")

    runs = data.get("run", []) if _problem("list of tables", data.get("run", [])) is None else []
    steps = data.get("step", []) if _problem("list of tables", data.get("step", [])) is None else []
    if bool(runs) == bool(steps):
        problems.append("give either [[run]] entries or [[step]] entries (one or more, not both)")
    for number, run in enumerate(runs, 1):
        where = f"run {number}: "
        _check(run, _RUN, where, problems)
        if "cmd" not in run:
            problems.append(f"{where}cmd is required")
        if "output" in run and "lines" in run:
            problems.append(f"{where}give output or lines, not both")
    for number, step in enumerate(steps, 1):
        where = f"step {number}: "
        _check(step, _STEP, where, problems)
        for key in ("at", "lines"):
            if key not in step:
                problems.append(f"{where}{key} is required")

    out = data.get("out", [f"{path.stem}.svg"])
    if not _problem("list of str", out):
        for name in out:
            if Path(name).suffix not in FORMATS:
                problems.append(f"out: {name!r} should end in .svg or .html")
    if problems:
        raise ClipError(path, problems)

    folder = path.parent
    return Clip(
        path=path,
        label=data["label"],
        out=[folder / name for name in out],
        record=Record(
            cwd=folder / record.get("cwd", "."),
            setup=record.get("setup", []),
            env=record.get("env", {}),
            timeout=record.get("timeout", 60),
        ),
        theme=THEME | theme,
        title=data.get("title", ""),
        cols=data.get("cols", 80),
        rows=data.get("rows"),
        prompt=data.get("prompt", DEFAULT_PROMPT),
        final_prompt=data.get("final_prompt"),
        typing_speed=data.get("typing_speed", 28),
        line_gap=data.get("line_gap", 0.07),
        hold=data.get("hold", 4.0),
        duration=data.get("duration"),
        chrome=data.get("chrome", True),
        runs=[
            Run(
                cmd=run["cmd"],
                exec=run.get("exec"),
                output=folder / run["output"] if "output" in run else None,
                lines=run.get("lines"),
                input=run.get("input"),
                record=run.get("record", True),
                prompt=run.get("prompt"),
                think=run.get("think", 0.5),
                pause=run.get("pause", 0.9),
                line_gap=run.get("line_gap"),
            )
            for run in runs
        ],
        steps=[Step(at=step["at"], lines=step["lines"], caret=step.get("caret", False)) for step in steps],
    )
