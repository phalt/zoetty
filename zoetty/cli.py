from pathlib import Path

import click
from rich.console import Console
from rich.markup import escape

from zoetty import clip as clips
from zoetty import html, record, svg, timeline
from zoetty.settings import VERSION

STARTER = """# A zoetty clip. Build it with: zoetty build {path}
# Every key is described at https://phalt.github.io/zoetty/clip-format/
title = "~/my-project"
label = "Saying hello in a terminal"
cols = 60

[[run]]
cmd = "echo 'Hello from zoetty!'"
lines = ["Hello from zoetty!"]

[[run]]
cmd = "ls"
lines = ["[blue]docs[/]  README.md  [green]tool.py[/]"]

# Record real output instead of writing it by hand:
# give a run an `output` file, then run `zoetty record {path}`.
#
# [[run]]
# cmd = "git log --oneline -3"
# output = "captures/git-log.ansi"
"""


def _console() -> Console:
    return Console(highlight=False, soft_wrap=True)


def _load(console: Console, path: Path) -> clips.Clip | None:
    try:
        return clips.load(path)
    except clips.ClipError as error:
        console.print(f"[red]✗ {escape(str(path))}[/]")
        for problem in error.problems:
            console.print(f"  [red]•[/] {escape(problem)}")
        return None


def _render(clip: clips.Clip) -> dict[Path, str]:
    """What each of the clip's output files should contain. Raises MissingCapture."""
    lines = timeline.build(clip)
    return {
        out: (svg.render if out.suffix == ".svg" else html.render)(clip, lines, timeline.name(out)) for out in clip.out
    }


@click.group()
@click.version_option(VERSION, prog_name="zoetty")
def cli() -> None:
    """⚜ zoetty: looping terminal clips as plain SVG or HTML and CSS."""


@cli.command()
@click.argument("spec", type=click.Path(dir_okay=False, path_type=Path))
def init(spec: Path) -> None:
    """Write a starter clip spec to SPEC."""
    console = _console()
    if spec.exists():
        raise click.ClickException(f"{spec} already exists")
    spec.parent.mkdir(parents=True, exist_ok=True)
    spec.write_text(STARTER.format(path=spec))
    console.print(f"[green]✓[/] wrote {escape(str(spec))}")
    console.print(f"  next: [bold]zoetty build {escape(str(spec))}[/]")


@cli.command()
@click.argument("specs", nargs=-1, required=True, type=click.Path(dir_okay=False, path_type=Path))
def build(specs: tuple[Path, ...]) -> None:
    """Render each clip spec to its output files."""
    console = _console()
    failed = False
    for path in specs:
        clip = _load(console, path)
        if clip is None:
            failed = True
            continue
        try:
            outputs = _render(clip)
        except timeline.MissingCapture as error:
            console.print(f"[red]✗ {escape(str(path))}[/]: {escape(str(error))}")
            failed = True
            continue
        for out, content in outputs.items():
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content)
            console.print(f"[green]✓[/] {escape(str(out))} [dim]({len(content.encode()) / 1024:.1f}KB)[/]")
    if failed:
        raise SystemExit(1)


@cli.command()
@click.argument("specs", nargs=-1, required=True, type=click.Path(dir_okay=False, path_type=Path))
def check(specs: tuple[Path, ...]) -> None:
    """Fail if a clip spec is broken, or its output files are missing or out of date."""
    console = _console()
    failed = False
    for path in specs:
        clip = _load(console, path)
        if clip is None:
            failed = True
            continue
        try:
            outputs = _render(clip)
        except timeline.MissingCapture as error:
            console.print(f"[red]✗ {escape(str(path))}[/]: {escape(str(error))}")
            failed = True
            continue
        stale = [out for out, content in outputs.items() if not out.exists() or out.read_text() != content]
        if stale:
            failed = True
            for out in stale:
                why = "is out of date" if out.exists() else "doesn't exist"
                console.print(f"[red]✗ {escape(str(out))}[/] {why}: run [bold]zoetty build {escape(str(path))}[/]")
        else:
            console.print(f"[green]✓[/] {escape(str(path))}")
    if failed:
        raise SystemExit(1)


@cli.command(name="record")
@click.argument("specs", nargs=-1, required=True, type=click.Path(dir_okay=False, path_type=Path))
def record_(specs: tuple[Path, ...]) -> None:
    """Run each clip's commands for real and save their output."""
    console = _console()
    failed = False
    for path in specs:
        clip = _load(console, path)
        if clip is None:
            failed = True
            continue
        runs = [run for run in clip.runs if run.recordable]
        if not runs:
            console.print(f"[yellow]•[/] {escape(str(path))}: nothing to record (no run has an output file)")
            continue
        console.print(f"[bold]{escape(str(path))}[/]")
        env = record.environment(clip)
        try:
            record.setup(clip, env)
        except record.SetupFailed as error:
            console.print(f"  [red]✗ setup:[/] {escape(error.command)} exited {error.exit_code}")
            console.print(escape(error.output.rstrip()), style="dim")
            failed = True
            continue
        for run in runs:
            assert run.output is not None
            result = record.run(
                run.command,
                cwd=clip.record.cwd,
                env=env,
                cols=clip.cols,
                rows=clip.rows or 24,
                input=run.input,
                timeout=clip.record.timeout,
            )
            if result.timed_out:
                console.print(f"  [red]✗ {escape(run.cmd)}[/] timed out after {clip.record.timeout:g}s")
                failed = True
                break
            run.output.parent.mkdir(parents=True, exist_ok=True)
            run.output.write_bytes(result.output)
            mark = "[green]✓[/]" if result.exit_code == 0 else "[yellow]![/]"
            console.print(f"  {mark} {escape(run.cmd)} [dim]· exit {result.exit_code} → {escape(str(run.output))}[/]")
    if failed:
        raise SystemExit(1)
