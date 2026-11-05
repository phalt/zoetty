# Implementation Plan: zoetty 0.1.0

Status: approved (2026-11-05)
Spec: [specs/SPEC.md](../specs/SPEC.md)
Tasks: [tasks/todo.md](todo.md)

## Overview

Turn the `termclip` prototype (a single script that rendered the paulrun and clientele clips) into a packaged CLI with paulrun's layout and standards. The prototype's renderers are proven; the work is splitting them into tested modules, adding `record`, `build`, `check` and `init`, and documenting it with clips zoetty makes itself.

## Architecture decisions

- **One data model, two renderers.** `clip.load(path) -> Clip` validates the TOML. `timeline.lines(clip) -> list[Line]` turns runs or steps into timed lines (each a list of styled `Segment`s, with optional typing and caret). `svg.render(clip, lines, name)` and `html.render(clip, lines, name)` only ever see `Line`s.
- **Names come from the output file.** Keyframe and class prefixes are derived from the output file's stem, so HTML fragments can share a page and builds stay deterministic.
- **Captures are markup-free ANSI files.** `record` writes exactly what the pty produced. `ansi.to_markup` converts at build time, so a converter fix improves every clip without re-recording.
- **Recording is plain functions over a pty.** `record.run(command, cwd, env, cols, rows, input, timeout) -> Result(exit_code, output)`. The CLI loops over runs and writes files. Tests run real `printf`/`sh` commands.
- **The CLI owns the terminal.** Only `cli.py` imports click and rich (import-linter contract), the same as paulrun.

## Dependency graph

```
scaffold (1) ── markup (2) ── ansi (3) ── clip loading (4) ── timeline (5) ─┬─ svg (6) ─┬─ build/check/init (8) ── docs + dogfood (10) ── release runbook (11)
                                                                           └─ html (7) ─┘        │
                                                                                       record (9) ┘
```

## Task list

Full task bodies are in [todo.md](todo.md).

1. Package skeleton, tooling, CI, `zoetty --version`
2. Markup parser
3. ANSI to markup
4. Clip spec loading and validation
5. Timeline: runs and steps to timed lines, scrolling
6. SVG renderer
7. HTML renderer
8. `init`, `build`, `check`
9. `record`
10. Docs site, examples, README with dogfood clips and agent prompt
11. `PUBLISHING.md` runbook, changelog, final checks

## Risks

- **pty behaviour differs on macOS.** Keep recording to `pty.openpty` + `subprocess`, which both support; CI only runs Linux, so note it in the docs if anything differs.
- **Font metrics in SVG.** Already handled by `textLength` per run; wide characters (emoji) may sit slightly off. Documented as a known limitation.
