"""Turn a clip into timed lines: what appears on screen, and when."""

import re
from dataclasses import dataclass
from pathlib import Path

from zoetty import ansi
from zoetty.clip import Clip
from zoetty.markup import Segment, escape, parse

START = 0.4
FADE = 0.6
MIN_TYPING, MAX_TYPING = 0.4, 2.2


class MissingCapture(Exception):
    """A run's output file hasn't been recorded yet."""

    def __init__(self, path: Path) -> None:
        self.path = path
        super().__init__(f"{path} doesn't exist yet: run `zoetty record` first")


@dataclass(frozen=True)
class Line:
    """One line of the screen: shown from `at`, with a caret until `caret_until` if set."""

    at: float
    segments: list[Segment]
    caret_until: float | None = None

    @property
    def columns(self) -> int:
        return sum(len(segment.text) for segment in self.segments)


@dataclass(frozen=True)
class Timeline:
    lines: list[Line]
    duration: float
    rows: int

    @property
    def fade(self) -> float:
        """When the screen starts fading out before the loop restarts."""
        return max(self.duration - FADE, 0)

    def scroll(self) -> list[tuple[float, int]]:
        """(time, rows scrolled) each time a line lands below the bottom of the screen."""
        return [(line.at, index - self.rows + 1) for index, line in enumerate(self.lines) if index >= self.rows]


def percent(seconds: float, total: float) -> str:
    """A time as a keyframe percentage of the loop."""
    return f"{min(seconds / total * 100, 100):.3f}%"


def name(path: Path) -> str:
    """A CSS-safe name for a clip, from its output file, used to prefix its keyframes and classes."""
    return "zt-" + re.sub(r"[^a-zA-Z0-9]+", "-", path.stem).strip("-").lower()


def wrap(segments: list[Segment], cols: int) -> list[list[Segment]]:
    """Split a line into rows of at most `cols` characters, the way a terminal wraps output."""
    rows: list[list[Segment]] = [[]]
    used = 0
    for segment in segments:
        text = segment.text
        while text:
            if used == cols:
                rows.append([])
                used = 0
            piece, text = text[: cols - used], text[cols - used :]
            rows[-1].append(Segment(piece, segment.styles, segment.typing, segment.delay))
            used += len(piece)
    return rows


def _from_runs(clip: Clip) -> tuple[list[Line], float]:
    steps: list[tuple[float, list[Segment], bool]] = []
    t = START
    for run in clip.runs:
        typing = min(max(len(run.cmd) / clip.typing_speed, MIN_TYPING), MAX_TYPING)
        prompt = clip.prompt if run.prompt is None else run.prompt
        steps.append((t, parse(f"{prompt}[type {typing:.2f}]{escape(run.cmd)}[/]"), True))
        t += 0.15 + typing + run.think
        if run.output is not None:
            if not run.output.exists():
                raise MissingCapture(run.output)
            output = ansi.to_markup(run.output.read_text(errors="replace"))
        else:
            output = run.lines or []
        gap = clip.line_gap if run.line_gap is None else run.line_gap
        for line in output:
            for row in wrap(parse(line), clip.cols):
                steps.append((round(t, 3), row, False))
                t += gap
        t += run.pause
    final = clip.prompt if clip.final_prompt is None else clip.final_prompt
    steps.append((round(t, 3), parse(final), True))
    duration = clip.duration or round(t + clip.hold, 2)
    return _lines(steps, duration), duration


def _from_steps(clip: Clip) -> tuple[list[Line], float]:
    ordered = sorted(clip.steps, key=lambda step: step.at)
    duration = clip.duration or round(ordered[-1].at + clip.hold, 2)
    steps = []
    for step in ordered:
        for index, line in enumerate(step.lines):
            steps.append((step.at, parse(line), step.caret and index == len(step.lines) - 1))
    return _lines(steps, duration), duration


def _lines(steps: list[tuple[float, list[Segment], bool]], duration: float) -> list[Line]:
    """Lines from (time, segments, has caret) steps. A caret lasts until the next line appears."""
    lines = []
    for index, (at, segments, caret) in enumerate(steps):
        later = [time for time, _, _ in steps[index + 1 :] if time > at]
        until = (later[0] if later else duration) if caret else None
        lines.append(Line(at, segments, until))
    return lines


def build(clip: Clip) -> Timeline:
    """Everything shown in the clip, with times in seconds. Raises MissingCapture."""
    lines, duration = _from_runs(clip) if clip.runs else _from_steps(clip)
    return Timeline(lines, duration, clip.rows or len(lines))
