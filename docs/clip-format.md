# 📜 Clip format

A clip is described by a TOML file, usually kept in `docs/clips/`. Paths in it are relative to the file.

The smallest clip has a `label` and one run:

```toml
label = "Listing the files in a project"

[[run]]
cmd = "ls"
lines = ["README.md  src  tests"]
```

`zoetty build` turns `clip.toml` into `clip.svg` next to it.

## Top-level keys

| Key | Default | What it does |
|---|---|---|
| `label` | required | What the clip shows, in words. Used as the alt text and `aria-label`, so people who can't see the animation still get it. |
| `title` | `""` | Shown in the window bar, like a terminal's title. |
| `cols` | `80` | Terminal width in columns. Recording uses it too, so output wraps where it would in a real terminal of that size. |
| `rows` | every line | Visible rows. Output scrolls once it passes this. |
| `out` | `["<name>.svg"]` | Files `zoetty build` writes. `.svg` makes an SVG image, `.html` an HTML fragment. |
| `prompt` | `"[dim]$[/] "` | Shown before each command. |
| `final_prompt` | `prompt` | Left blinking at the end. |
| `typing_speed` | `28` | Characters per second commands are typed at. Typing always takes between 0.4 and 2.2 seconds. |
| `line_gap` | `0.07` | Seconds between output lines. |
| `hold` | `4.0` | Seconds the last frame is held before the clip loops. |
| `duration` | worked out | Total loop length in seconds, if you'd rather set it. |
| `chrome` | `true` | Draw the window bar with its dots and title. |

## `[[run]]`: commands

Each run is a command typed at the prompt, followed by its output. Runs are shown in order.

```toml
[[run]]
cmd = "clientele start-api -f schema.json -o my_client/"
output = "captures/start-api.ansi"
```

| Key | Default | What it does |
|---|---|---|
| `cmd` | required | The command typed on screen. |
| `output` | | A file holding the command's captured output. `zoetty record` writes it. |
| `lines` | | Output written by hand, one [markup](#markup) string per line. |
| `exec` | `cmd` | What `zoetty record` actually runs, when it's different from what's shown (e.g. `.venv/bin/tool` instead of `tool`, or `cd demo && tool`). |
| `input` | | Text typed into the command while recording. Each line is typed once the command has been quiet for a moment, so it lands after the prompt that asked for it. Then Ctrl-D is sent, which ends a REPL. |
| `record` | `true` | Set to `false` to keep an `output` file but never re-record it. |
| `prompt` | the clip's | A different prompt for this command, e.g. `">>> "` inside a REPL. |
| `think` | `0.5` | Seconds between finishing typing and the output appearing. |
| `pause` | `0.9` | Seconds after the output before the next command. |
| `line_gap` | the clip's | Seconds between this run's output lines. |

A run has `output` or `lines`, not both. A run with neither shows no output.

Output lines wider than `cols` wrap onto the next row, as they would in a terminal.

## `[record]`: how commands are recorded

```toml
[record]
cwd = "../.."                       # run from the repo root
setup = ["rm -rf my_client"]        # run first, output not shown
env = { NO_COLOR = "" }
timeout = 120
```

| Key | Default | What it does |
|---|---|---|
| `cwd` | the spec's folder | Where commands run. |
| `setup` | `[]` | Shell commands run before the first recorded command, to start from a known state. Recording stops if one fails. |
| `env` | `{}` | Extra environment variables. |
| `timeout` | `60` | Seconds each command may take. |

Commands also get `TERM=xterm-256color`, `COLUMNS` and `LINES` from the clip's size, `FORCE_COLOR=1` and `CLICOLOR_FORCE=1` so they keep their colours, and `PAGER=cat` and `GIT_PAGER=cat` so nothing waits on a pager. `env` can override any of them.

A command that exits non-zero is recorded like any other (failing commands make good demos too); `zoetty record` shows its exit code.

## `[theme]`: colours

```toml
[theme]
bg = "#282c34"
bar = "#21252b"
fg = "#abb2bf"
green = "#98c379"
```

`bg`, `fg` (text), `bar` (window bar) and the six colours `blue`, `green`, `yellow`, `red`, `cyan` and `magenta`, as `#rgb` or `#rrggbb`. Anything you don't set keeps its default.

## Markup

`lines`, `prompt` and `final_prompt` use a small markup, a lot like [rich](https://rich.readthedocs.io/)'s:

| Markup | Shows |
|---|---|
| `[bold]text[/]` | Styled text. Styles are `bold`, `dim`, `italic`, and the colours `blue`, `green`, `yellow`, `red`, `cyan` and `magenta`. |
| `[bold green]text[/]` | Several styles at once. |
| `\[` | A literal `[`. In TOML strings write `\\[`, or use single-quoted strings: `'\[y/N]'`. |
| `[type 1.2]text[/]` | Text typed out over 1.2 seconds. `[type 1.2 0.5]` waits 0.5 seconds first. Only needed in `[[step]]` clips: commands in runs are typed for you. |

Captured output is converted to markup automatically: colours and bold, dim and italic are kept; cursor movement and other escape codes are dropped.

## `[[step]]`: hand-timed clips

For clips that aren't a series of commands, give `[[step]]` entries instead of `[[run]]`s, saying exactly when lines appear. A clip has runs or steps, not both.

```toml
label = "A prompt being answered"
duration = 6

[[step]]
at = 0.5
lines = ['Start? \[y/N] [type 0.1 0.8]y[/]']
caret = true

[[step]]
at = 2
lines = ["[green]✓ started[/]"]
```

| Key | Default | What it does |
|---|---|---|
| `at` | required | Seconds into the clip the lines appear. |
| `lines` | required | Markup lines. |
| `caret` | `false` | Show a blinking caret at the end of the last line, until the next step. |

## Limitations

- zoetty reads output line by line rather than emulating a terminal. Colours are kept and a carriage return keeps what was last written on the line (so simple spinners end up showing their final state), but full-screen programs and progress bars that move the cursor won't look right.
- Wide characters such as emoji take one column in zoetty's layout but two in most terminals, so text after them can sit slightly off.
