import pytest
from click.testing import CliRunner

from zoetty.cli import cli
from zoetty.settings import VERSION

STATIC = """
label = "Static"
out = ["static.svg", "web/static.html"]
[[run]]
cmd = "echo hi"
lines = ["hi"]
"""

RECORDED = """
label = "Recorded"
[record]
setup = ["echo prepared > state"]
[[run]]
cmd = "show-state"
exec = "cat state; printf '\\\\033[31mred\\\\033[0m\\\\n'"
output = "captures/state.ansi"
[[run]]
cmd = "skipped"
output = "captures/kept.ansi"
record = false
[[run]]
cmd = "fails"
exec = "exit 2"
output = "captures/fails.ansi"
[[run]]
cmd = "by hand"
lines = ["x"]
"""


@pytest.fixture
def invoke():
    def go(*args):
        return CliRunner().invoke(cli, list(args))

    return go


def test_version(invoke):
    result = invoke("--version")
    assert result.exit_code == 0 and result.output == f"zoetty, version {VERSION}\n"


def test_init_writes_a_starter_that_builds(invoke, tmp_path):
    result = invoke("init", "clips/hello.toml")
    assert result.exit_code == 0 and "wrote clips/hello.toml" in result.output
    assert "zoetty build clips/hello.toml" in (tmp_path / "clips/hello.toml").read_text()
    assert invoke("build", "clips/hello.toml").exit_code == 0
    assert (tmp_path / "clips/hello.svg").exists()


def test_init_never_overwrites(invoke, spec):
    path = spec(STATIC)
    result = invoke("init", str(path))
    assert result.exit_code == 1 and "already exists" in result.output
    assert path.read_text().strip().startswith('label = "Static"')


def test_build_writes_every_output(invoke, spec, tmp_path):
    spec(STATIC)
    result = invoke("build", "clip.toml")
    assert result.exit_code == 0
    assert (tmp_path / "static.svg").read_text().startswith("<svg")
    assert (tmp_path / "web/static.html").read_text().startswith('<div class="zt-static"')
    assert "✓ static.svg" in result.output and "✓ web/static.html" in result.output and "KB)" in result.output


def test_build_reports_broken_specs_and_carries_on(invoke, spec, tmp_path):
    spec('cols = "wide"', name="broken.toml")
    spec('label = "x"\n[[run]]\ncmd = "go"\noutput = "nope.ansi"\n', name="unrecorded.toml")
    spec(STATIC)
    result = invoke("build", "broken.toml", "unrecorded.toml", "clip.toml")
    assert result.exit_code == 1
    assert "✗ broken.toml" in result.output and "cols should be a positive int" in result.output
    assert "✗ unrecorded.toml" in result.output and "run `zoetty record` first" in result.output
    assert (tmp_path / "static.svg").exists()


def test_check(invoke, spec, tmp_path):
    spec(STATIC)
    result = invoke("check", "clip.toml")
    assert result.exit_code == 1 and "static.svg doesn't exist: run zoetty build clip.toml" in result.output

    invoke("build", "clip.toml")
    result = invoke("check", "clip.toml")
    assert result.exit_code == 0 and result.output == "✓ clip.toml\n"

    (tmp_path / "web/static.html").write_text("edited")
    result = invoke("check", "clip.toml")
    assert result.exit_code == 1 and "web/static.html is out of date" in result.output


def test_check_reports_broken_and_unrecorded_specs(invoke, spec):
    spec("label = 1", name="broken.toml")
    spec('label = "x"\n[[run]]\ncmd = "go"\noutput = "nope.ansi"\n', name="unrecorded.toml")
    result = invoke("check", "broken.toml", "unrecorded.toml")
    assert result.exit_code == 1
    assert "✗ broken.toml" in result.output and "run `zoetty record` first" in result.output


def test_record_runs_setup_then_each_recordable_run(invoke, spec, tmp_path):
    spec(RECORDED)
    result = invoke("record", "clip.toml")
    assert result.exit_code == 0, result.output
    assert (tmp_path / "captures/state.ansi").read_bytes() == b"prepared\r\n\x1b[31mred\x1b[0m\r\n"
    assert not (tmp_path / "captures/kept.ansi").exists()
    assert (tmp_path / "captures/fails.ansi").read_bytes() == b""
    assert "✓ show-state · exit 0 → captures/state.ansi" in result.output
    assert "! fails · exit 2" in result.output and "skipped" not in result.output

    (tmp_path / "captures/kept.ansi").write_text("kept\n")
    assert invoke("build", "clip.toml").exit_code == 0


def test_record_with_nothing_to_record(invoke, spec):
    spec(STATIC)
    result = invoke("record", "clip.toml")
    assert result.exit_code == 0 and "nothing to record" in result.output


def test_record_stops_a_clip_when_setup_fails(invoke, spec, tmp_path):
    spec('label = "x"\n[record]\nsetup = ["echo broken; exit 1"]\n[[run]]\ncmd = "go"\noutput = "a.ansi"\n')
    result = invoke("record", "clip.toml")
    assert result.exit_code == 1 and "✗ setup: echo broken; exit 1 exited 1" in result.output
    assert "broken" in result.output and not (tmp_path / "a.ansi").exists()


def test_record_stops_a_clip_on_timeout(invoke, spec, tmp_path):
    spec(
        'label = "x"\n[record]\ntimeout = 0.5\n'
        '[[run]]\ncmd = "slow"\nexec = "sleep 5"\noutput = "a.ansi"\n'
        '[[run]]\ncmd = "next"\noutput = "b.ansi"\n'
    )
    result = invoke("record", "clip.toml")
    assert result.exit_code == 1 and "✗ slow timed out after 0.5s" in result.output
    assert not (tmp_path / "b.ansi").exists()


def test_record_reports_broken_specs(invoke, spec):
    spec("nope", name="broken.toml")
    result = invoke("record", "broken.toml")
    assert result.exit_code == 1 and "isn't valid TOML" in result.output
