from pathlib import Path

import pytest

from zoetty.clip import DEFAULT_PROMPT, THEME, ClipError, load

MINIMAL = """
label = "A clip"

[[run]]
cmd = "ls"
"""


def problems(path: Path) -> list[str]:
    with pytest.raises(ClipError) as error:
        load(path)
    assert str(path) in str(error.value)
    return error.value.problems


def test_minimal_spec_gets_defaults(spec, tmp_path):
    clip = load(spec(MINIMAL))
    assert clip.label == "A clip"
    assert clip.out == [tmp_path / "clip.svg"]
    assert (clip.cols, clip.rows, clip.title, clip.chrome) == (80, None, "", True)
    assert clip.prompt == DEFAULT_PROMPT and clip.final_prompt is None
    assert clip.theme == THEME
    assert clip.record.cwd == tmp_path and clip.record.setup == [] and clip.record.env == {}
    assert clip.record.timeout == 60
    [run] = clip.runs
    assert run.command == "ls" and not run.recordable and run.lines is None


def test_every_key(spec, tmp_path):
    clip = load(
        spec(
            """
            title = "~/x"
            label = "Everything"
            cols = 72
            rows = 10
            out = ["a.svg", "web/a.html"]
            prompt = "[bold]>[/] "
            final_prompt = "> "
            typing_speed = 40
            line_gap = 0.1
            hold = 2
            duration = 30
            chrome = false

            [record]
            cwd = "work"
            setup = ["rm -rf out"]
            env = { NAME = "Paul" }
            timeout = 5

            [theme]
            bg = "#282c34"
            red = "#e06"

            [[run]]
            cmd = "tool go"
            exec = ".venv/bin/tool go"
            output = "captures/go.ansi"
            input = "y\\n"
            prompt = ">>> "
            think = 0
            pause = 1.5
            line_gap = 0.2

            [[run]]
            cmd = "tool stop"
            output = "captures/stop.ansi"
            record = false

            [[run]]
            cmd = "echo hi"
            lines = ["[green]hi[/]"]
            """
        )
    )
    assert clip.out == [tmp_path / "a.svg", tmp_path / "web/a.html"]
    assert (clip.cols, clip.rows, clip.typing_speed, clip.line_gap, clip.hold, clip.duration) == (
        72,
        10,
        40,
        0.1,
        2,
        30,
    )
    assert clip.chrome is False and clip.final_prompt == "> " and clip.title == "~/x"
    assert clip.record.cwd == tmp_path / "work" and clip.record.env == {"NAME": "Paul"} and clip.record.timeout == 5
    assert clip.theme["bg"] == "#282c34" and clip.theme["red"] == "#e06" and clip.theme["fg"] == THEME["fg"]
    go, stop, echo = clip.runs
    assert go.command == ".venv/bin/tool go" and go.output == tmp_path / "captures/go.ansi" and go.recordable
    assert (go.input, go.prompt, go.think, go.pause, go.line_gap) == ("y\n", ">>> ", 0, 1.5, 0.2)
    assert not stop.recordable
    assert echo.lines == ["[green]hi[/]"] and not echo.recordable


def test_steps(spec):
    clip = load(
        spec(
            """
            label = "Steps"
            [[step]]
            at = 0.5
            lines = ["one", "two"]
            caret = true
            [[step]]
            at = 2
            lines = ["three"]
            """
        )
    )
    assert [(step.at, step.lines, step.caret) for step in clip.steps] == [
        (0.5, ["one", "two"], True),
        (2, ["three"], False),
    ]
    assert clip.runs == []


def test_unreadable_and_invalid_files(tmp_path):
    assert problems(tmp_path / "missing.toml") == ["can't read it: No such file or directory"]
    bad = tmp_path / "bad.toml"
    bad.write_text("label = ")
    assert problems(bad)[0].startswith("isn't valid TOML")


def test_every_problem_is_reported_at_once(spec):
    found = problems(
        spec(
            """
            cols = 0
            rows = true
            out = ["a.png"]
            prompt = "[blink]$[/]"
            hold = -1
            chrome = "yes"
            surprise = 1

            [record]
            setup = "not a list"
            env = { A = 1 }
            nope = 1

            [theme]
            pink = "#fff"
            bg = "black"

            [[run]]
            output = "a.ansi"
            lines = ["x"]

            [[run]]
            cmd = 3
            lines = ["[wobble]x"]
            """
        )
    )
    expected = [
        "cols should be a positive int, got 0",
        "rows should be a positive int, got True",
        "prompt unknown style '[blink]'",
        "hold should be a number, 0 or more, got -1",
        "chrome should be a bool, got 'yes'",
        "unknown key 'surprise'",
        "label is required",
        "record.setup should be a list of str",
        "record.env should be a table of str",
        "record.unknown key 'nope'",
        "theme.pink isn't a theme colour",
        "theme.bg should be a colour like '#282c34', got 'black'",
        "run 1: cmd is required",
        "run 1: give output or lines, not both",
        "run 2: cmd should be a str",
        "run 2: lines unknown style '[wobble]'",
        "out: 'a.png' should end in .svg or .html",
    ]
    for problem in expected:
        assert any(found_problem.startswith(problem) for found_problem in found), problem
    assert len(found) == len(expected)


def test_runs_or_steps_but_not_both_or_neither(spec):
    assert problems(spec('label = "x"')) == ["give either [[run]] entries or [[step]] entries (one or more, not both)"]
    both = spec(
        """
        label = "x"
        [[run]]
        cmd = "ls"
        [[step]]
        at = 1
        lines = ["x"]
        """
    )
    assert problems(both) == ["give either [[run]] entries or [[step]] entries (one or more, not both)"]


def test_wrongly_shaped_tables_are_reported_not_crashed_on(spec):
    found = problems(spec('label = "x"\nrecord = 1\ntheme = 2\nrun = 3\nout = "a.svg"'))
    assert "record should be a table, got 1" in found
    assert "theme should be a table, got 2" in found
    assert "run should be a list of tables, got 3" in found
    assert "out should be a list of str, got 'a.svg'" in found


def test_step_problems(spec):
    found = problems(
        spec(
            """
            label = "x"
            [[step]]
            caret = 1
            """
        )
    )
    assert found == ["step 1: caret should be a bool, got 1", "step 1: at is required", "step 1: lines is required"]


def test_list_of_markup_must_be_a_list_of_strings(spec):
    found = problems(spec('label = "x"\n[[run]]\ncmd = "ls"\nlines = "hi"\n'))
    assert found == ["run 1: lines should be a list of markup, got 'hi'"]
