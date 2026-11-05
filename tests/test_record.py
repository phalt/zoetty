import os

import pytest

from zoetty import record
from zoetty.clip import load


def run(command, tmp_path, **kwargs):
    kwargs.setdefault("env", dict(os.environ))
    return record.run(command, cwd=tmp_path, cols=kwargs.pop("cols", 50), rows=kwargs.pop("rows", 10), **kwargs)


def test_captures_output_and_exit_code(tmp_path):
    result = run("printf '\\033[32mok\\033[0m\\n'; exit 3", tmp_path)
    assert result.output == b"\x1b[32mok\x1b[0m\r\n"
    assert result.exit_code == 3 and not result.timed_out


def test_runs_in_a_terminal_of_the_given_size(tmp_path):
    result = run("test -t 1 && stty size", tmp_path, cols=73, rows=11)
    assert result.output.strip() == b"11 73"


def test_input_is_typed_after_each_prompt(tmp_path):
    script = "printf 'Name? '; read name; printf 'Sure? '; read sure; echo \"$name $sure\""
    result = run(script, tmp_path, input="Paul\ny\n")
    assert result.output == b"Name? Paul\r\nSure? y\r\nPaul y\r\n"


def test_runs_in_the_working_folder_with_the_environment(tmp_path):
    result = run('pwd; echo "$GREETING"', tmp_path, env=dict(os.environ, GREETING="hi"))
    assert result.output.split() == [str(tmp_path).encode(), b"hi"]


def test_timeout_kills_the_command(tmp_path):
    result = run("echo started; sleep 30", tmp_path, timeout=0.5)
    assert result.timed_out and result.exit_code is None
    assert b"started" in result.output


def test_a_background_process_holding_the_terminal_does_not_hang_recording(tmp_path):
    result = run("(sleep 2 &) ; echo done", tmp_path, timeout=10)
    assert result.output.strip() == b"done" and result.exit_code == 0


def test_environment_forces_colour_and_size_and_disables_pagers(spec):
    clip = load(spec('label = "x"\ncols = 70\nrows = 9\n[record]\nenv = { PAGER = "less" }\n[[run]]\ncmd = "ls"\n'))
    env = record.environment(clip)
    assert env["COLUMNS"] == "70" and env["LINES"] == "9" and env["FORCE_COLOR"] == "1"
    assert env["GIT_PAGER"] == "cat" and env["TERM"] == "xterm-256color"
    assert env["PAGER"] == "less"  # the clip's own env wins
    assert record.environment(load(spec('label = "x"\n[[run]]\ncmd = "ls"\n')))["LINES"] == "24"


def test_setup_runs_in_order_and_stops_on_failure(spec, tmp_path):
    clip = load(
        spec(
            'label = "x"\n[[run]]\ncmd = "ls"\n'
            '[record]\nsetup = ["echo one > a", "cat a > b", "echo oops; exit 4", "touch c"]\n'
        )
    )
    with pytest.raises(record.SetupFailed) as error:
        record.setup(clip, record.environment(clip))
    assert (tmp_path / "b").read_text() == "one\n" and not (tmp_path / "c").exists()
    assert (error.value.command, error.value.exit_code, error.value.output) == ("echo oops; exit 4", 4, "oops\n")


def test_end_of_input_is_sent_once_input_runs_out(tmp_path):
    # cat would wait for ever; after the last line of input it gets Ctrl-D, like a person ending a session.
    result = run("cat; echo finished", tmp_path, input="hi\n", timeout=10)
    assert result.output.endswith(b"finished\r\n") and not result.timed_out
    assert b"^D" not in result.output  # control characters aren't echoed as ^D


def test_no_end_of_input_without_input(tmp_path):
    result = run("cat", tmp_path, timeout=1)
    assert result.timed_out


def test_a_program_that_shows_the_end_of_input_still_has_no_marker(tmp_path):
    # Python's REPL prints ^D itself when it gets end of input; only that one is dropped.
    result = run("cat; printf '^Dbye ^D'", tmp_path, input="hi\n", timeout=10)
    assert result.output.endswith(b"bye ^D")
