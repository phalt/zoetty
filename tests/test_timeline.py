from pathlib import Path

import pytest

from zoetty import timeline
from zoetty.clip import load
from zoetty.markup import Segment, plain


def text(line: timeline.Line) -> str:
    return plain(line.segments)


def test_runs_become_typed_commands_output_and_a_final_prompt(spec):
    clip = load(
        spec(
            """
            label = "x"
            hold = 2
            [[run]]
            cmd = "echo hi"
            lines = ["hi", "[green]there[/]"]
            [[run]]
            cmd = "true"
            """
        )
    )
    built = timeline.build(clip)
    assert [text(line) for line in built.lines] == ["$ echo hi", "hi", "there", "$ true", "$ "]
    command = built.lines[0]
    assert command.at == timeline.START
    assert command.segments[-1] == Segment("echo hi", (), timeline.MIN_TYPING, 0.15)
    # The caret stays on a command line until the next line appears.
    assert command.caret_until == built.lines[1].at
    assert built.lines[1].caret_until is None
    assert built.lines[2].at - built.lines[1].at == pytest.approx(0.07)
    # The last prompt keeps its caret to the end, and the clip holds before looping.
    assert built.lines[-1].caret_until == built.duration
    assert built.duration == pytest.approx(built.lines[-1].at + 2)
    assert built.fade == pytest.approx(built.duration - timeline.FADE)
    assert built.rows == 5 and built.scroll() == []


def test_typing_time_is_clamped(spec):
    long = "x" * 500
    clip = load(spec(f'label = "x"\ntyping_speed = 10\n[[run]]\ncmd = "{long}"\n'))
    assert timeline.build(clip).lines[0].segments[-1].typing == timeline.MAX_TYPING


def test_command_text_is_shown_literally(spec):
    clip = load(spec('label = "x"\n[[run]]\ncmd = "echo [bold]"\n'))
    assert text(timeline.build(clip).lines[0]) == "$ echo [bold]"


def test_per_run_settings_and_prompts(spec):
    clip = load(
        spec(
            """
            label = "x"
            final_prompt = "[bold magenta]>>>[/] "
            line_gap = 1
            [[run]]
            cmd = "python"
            prompt = "% "
            think = 0
            pause = 0
            line_gap = 0.5
            lines = ["a", "b"]
            """
        )
    )
    lines = timeline.build(clip).lines
    assert text(lines[0]) == "% python" and text(lines[-1]) == ">>> "
    assert lines[2].at - lines[1].at == pytest.approx(0.5)
    assert lines[3].at == pytest.approx(lines[2].at + 0.5)


def test_captured_output_is_converted(spec, tmp_path):
    (tmp_path / "out.ansi").write_bytes(b"\x1b[32mok\x1b[0m\r\n\xff\r\n")
    clip = load(spec('label = "x"\n[[run]]\ncmd = "go"\noutput = "out.ansi"\n'))
    lines = timeline.build(clip).lines
    assert lines[1].segments == [Segment("ok", ("green",))]
    assert text(lines[2]) == "�"


def test_missing_capture(spec, tmp_path):
    clip = load(spec('label = "x"\n[[run]]\ncmd = "go"\noutput = "out.ansi"\n'))
    with pytest.raises(timeline.MissingCapture, match="run `zoetty record` first") as error:
        timeline.build(clip)
    assert error.value.path == tmp_path / "out.ansi"


def test_explicit_duration_wins(spec):
    clip = load(spec('label = "x"\nduration = 99\n[[run]]\ncmd = "ls"\n'))
    assert timeline.build(clip).duration == 99


def test_steps_are_sorted_and_carets_last_until_the_next_step(spec):
    clip = load(
        spec(
            """
            label = "x"
            hold = 1
            [[step]]
            at = 3
            lines = ["later"]
            caret = true
            [[step]]
            at = 1
            lines = ["first", "[type 0.5]typed[/]"]
            caret = true
            """
        )
    )
    built = timeline.build(clip)
    assert [(line.at, text(line), line.caret_until) for line in built.lines] == [
        (1, "first", None),
        (1, "typed", 3),
        (3, "later", 4),
    ]
    assert built.duration == 4


def test_rows_scroll(spec):
    lines = ", ".join(f'"{n}"' for n in range(6))
    clip = load(spec(f'label = "x"\nrows = 4\n[[run]]\ncmd = "seq"\nlines = [{lines}]\n'))
    built = timeline.build(clip)
    # 8 lines (command, 6 output, prompt) in 4 rows: scrolls once for each of the last 4.
    assert built.rows == 4
    assert [rows for _, rows in built.scroll()] == [1, 2, 3, 4]
    assert built.scroll()[0][0] == built.lines[4].at


def test_percent_and_name():
    assert timeline.percent(5, 10) == "50.000%"
    assert timeline.percent(20, 10) == "100.000%"
    assert timeline.name(Path("docs/clips/Start API.v2.svg")) == "zt-start-api-v2"
    assert timeline.Line(0, [Segment("ab"), Segment("c")]).columns == 3


def test_lines_wider_than_the_terminal_wrap(spec):
    clip = load(spec('label = "x"\ncols = 4\n[[run]]\ncmd = "x"\nlines = ["ab[green]cdefg[/]h", "abcd"]\n'))
    lines = timeline.build(clip).lines
    assert [line.segments for line in lines[1:4]] == [
        [Segment("ab"), Segment("cd", ("green",))],
        [Segment("efg", ("green",)), Segment("h")],
        [Segment("abcd")],
    ]
    assert lines[1].at < lines[2].at < lines[3].at


def test_wrap_keeps_empty_lines():
    assert timeline.wrap([], 10) == [[]]
