# Spec: zoetty

Status: approved (2026-11-05)
Version target: 0.1.0

## Objective

`zoetty` turns terminal sessions into small, looping, animated clips made of plain SVG or HTML and CSS. No video, no GIF, no JavaScript.

You describe a clip in a TOML file: the commands to show and where their output comes from. `zoetty record` runs the commands for real in a pseudo-terminal and keeps their coloured output. `zoetty build` renders the clip. The SVG works anywhere an image does (GitHub READMEs, PyPI, docs sites); the HTML fragment drops into any page you control. Both stay sharp at any size, are a few KB, and can be regenerated whenever the tool they demo changes.

**User:** Paul, for the docs of paulrun, clientele and clientele.dev, where it has already been proven with a prototype (`termclip`). Published to PyPI with a proper README and docs so other people, and their coding agents, can use it.

**Why:** Terminal GIFs go stale (clientele's showed a command that no longer exists) and are a pain to re-record. Hand-built CSS clips look great but drift from the real output. zoetty keeps the clip's source in the repo and the output real.

### User stories

- As Paul, I run `zoetty init docs/clips/hello.toml` and get a working starter clip to edit.
- As Paul, I run `zoetty record docs/clips/start-api.toml` and the real coloured output of each command is saved next to the spec.
- As Paul, I run `zoetty build docs/clips/*.toml` and get an `.svg` for the README and an `.html` fragment for the docs, from the same spec.
- As Paul, I run `zoetty check docs/clips/*.toml` in CI and it fails if a clip's spec is broken or a built file is out of date.
- As a coding agent, I'm asked "use zoetty to make a demo of this CLI", read the docs page for agents, write a spec, record, build and embed it without help.

## Decisions

1. **CLI first.** Capturing real output is the valuable part, and a static website can't run commands. A web playground may come later and would reuse the renderers.
2. **Specs are TOML** (stdlib `tomllib`), captures are plain files next to the spec, and built files are committed. Everything is a file you own.
3. **Timing is generated, not recorded.** Commands are typed at a steady speed and output lines appear with a small stagger. Real timing makes boring clips (long pauses, instant dumps). Per-run knobs adjust it.
4. **No terminal emulation in 0.1.0.** Output is read line by line: colours and styles are kept, cursor movement is dropped, and a carriage return keeps what was last written on that line (enough for simple spinners). Full-screen programs aren't supported.
5. Same stack and layout as paulrun: Python >= 3.12, Click, rich, hatchling, uv, ruff, ty, pytest, import-linter, mkdocs-material, MIT licence. macOS and Linux only (recording needs a pty).

## Clip spec format

This is the contract. Changes to it need sign-off (see Boundaries).

```toml
title = "~/my-project"          # optional, shown in the window bar
label = "What the clip shows"    # required, used as alt text / aria-label
cols = 80                        # optional, terminal width in columns, default 80
rows = 20                        # optional, visible rows; output scrolls past this. Default: all lines
out = ["start-api.svg", "start-api.html"]   # optional, files `build` writes, relative to the spec.
                                            # Default ["<spec stem>.svg"]. .svg -> SVG, .html -> HTML fragment
prompt = "[dim]$[/] "            # optional, prompt shown before each command
final_prompt = "[dim]$[/] "      # optional, prompt left blinking at the end. Default: prompt
typing_speed = 28                # optional, characters per second
line_gap = 0.07                  # optional, seconds between output lines
hold = 4.0                       # optional, seconds to hold the last frame before looping
chrome = true                    # optional, draw the window bar

[record]                         # optional, how `record` runs commands
cwd = "."                        # relative to the spec
setup = ["rm -rf my_client"]     # shell commands run first, output not shown
env = { NO_COLOR = "" }          # extra environment
timeout = 60                     # seconds per command

[theme]                          # optional, any of: bg fg bar blue green yellow red cyan magenta
bg = "#282c34"

[[run]]                          # one or more, shown in order
cmd = "clientele start-api -f schema.json -o my_client/"   # what is typed on screen
exec = ".venv/bin/clientele start-api ..."                  # optional, what `record` actually runs. Default: cmd
output = "captures/start-api-1.ansi"                        # optional, captured output file, relative to the spec
lines = ["'pikachu'"]                                       # optional, output written by hand in markup
input = "Paul\ny\n"                                         # optional, typed into the pty while recording
record = true                                               # optional, false skips this run when recording
prompt = "[bold magenta]>>>[/] "                            # optional, overrides the clip's prompt
think = 0.5                                                 # optional, pause after typing before output
pause = 0.9                                                 # optional, pause after output
line_gap = 0.07                                             # optional, overrides the clip's line_gap
```

- A run has at most one of `output` and `lines`. A run with neither shows no output.
- `record` runs every run that has `output` (unless `record = false`), in order, in one working folder, and writes the capture to `output`. Runs with `lines` are never executed.
- `build` fails with a clear message if an `output` file doesn't exist yet ("run `zoetty record` first").
- Output lines (captured or `lines`) wider than `cols` wrap onto the next row, as in a terminal.

### Markup

Used in `lines`, `prompt` and `final_prompt`. Captures are converted to it.

- `[style ...]text[/]` where styles are `bold dim italic` and the colours `blue green yellow red cyan magenta`, in any combination.
- `[type SECONDS]text[/]` types the text out; `[type SECONDS DELAY]` waits first. Only used inside `step` timelines (below) and by zoetty itself.
- `\[` is a literal `[`.
- Unknown styles are an error, reported with the line they're on.

### Low-level timelines

Instead of `[[run]]`, a spec can give `[[step]]` entries (`at` seconds, `lines` list, optional `caret`), for clips that aren't command sessions. A spec has `run` or `step`, not both. This is what the paulrun prototype used.

## Outputs

- **SVG:** one self-contained file. Every text run is placed at its column with `textLength`, so alignment survives whatever monospace font the viewer has. Works inside `<img>`: no external fonts, no scripts, no `foreignObject`.
- **HTML fragment:** a `<div>` plus a `<style>`, no `<html>` wrapper. Text is selectable. All class and keyframe names are prefixed with an id derived from the output file name, so several clips can share one page.
- Both: loop forever, fade out before restarting, show the final frame with no animation under `prefers-reduced-motion`, and are byte-for-byte deterministic (so `check` can compare them).

## Commands

| Command | What it does |
|---|---|
| `zoetty init SPEC` | Write a starter spec (fails if the file exists). |
| `zoetty record SPEC...` | Run each spec's setup and recordable runs in a pty, write captures. Prints one line per run with its exit code. |
| `zoetty build SPEC...` | Render each spec to its `out` files. |
| `zoetty check SPEC...` | Validate each spec and fail if any `out` file is missing or differs from a fresh build. Exit 1 on any problem. |
| `zoetty --version` | Print the version. |

Recording sets `TERM=xterm-256color`, `COLUMNS`/`LINES` and the pty window size from the spec, `FORCE_COLOR=1`, and `PAGER=cat` / `GIT_PAGER=cat` so nothing waits on a pager. A non-zero exit is reported but doesn't stop recording (failing commands are valid demos). A timeout does stop it.

## Project structure

Mirrors paulrun: flat `zoetty/` package, `tests/`, `docs/`, `specs/`, `tasks/`, `examples/`, `Makefile`, `PUBLISHING.md` (a paulrun runbook), CI on 3.12-3.15-dev.

Modules, top to bottom (enforced with import-linter):

- `cli.py`: Click and rich, the only module that touches the terminal UI
- `record.py`: runs commands in a pty
- `svg.py`, `html.py`: renderers
- `timeline.py`: turns a clip into timed lines; shared timing/CSS helpers
- `clip.py`: loads and validates spec files
- `ansi.py`, `markup.py`: text formats
- `settings.py`: version

## Docs

mkdocs-material site on GitHub Pages, dark theme default, with:

- Home: what it is, a live clip, quick start
- Install
- Clip format (the spec above, as a reference)
- Command line
- Embedding: SVG in READMEs / PyPI, HTML fragments in docs sites, themes
- Examples: from a two-line static clip up to recorded, interactive, scrolling, themed clips. Each one shown live, from specs in `docs/clips/` that zoetty builds and `check`s in the test suite
- Using zoetty with a coding agent: a copy-paste prompt and the workflow an agent should follow

The README dogfoods zoetty: its demos are SVGs built by zoetty from `docs/clips/`, and it has a "Use it with your coding agent" section with a copy-paste prompt.

## Testing

pytest, 100% line and branch coverage. Recording is tested with real ptys running small shell commands. A docs test builds every clip in `docs/clips/` and fails if any committed output is stale.

## Boundaries

- **Always:** keep the spec format backwards compatible within 0.x minor releases, or call it out in the changelog; keep outputs deterministic; keep coverage at 100%.
- **Ask first:** changing the spec format, adding runtime dependencies, adding JavaScript to any output.
- **Never:** network access at build time, external fonts or assets in outputs.

## Later (not 0.1.0)

- `zoetty preview` with live reload
- Real recorded timing as an option
- Terminal emulation for cursor-heavy output
- Light theme preset and `prefers-color-scheme` aware HTML
- A static web playground reusing the renderers
