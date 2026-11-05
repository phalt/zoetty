# zoetty 0.1.0 tasks

Status: done, CI green (2026-11-05). Not yet released: run `PUBLISHING.md` with VERSION=0.1.0.

Plan: [tasks/plan.md](plan.md). Spec: [specs/SPEC.md](../specs/SPEC.md).

Every task also clears the standing bar: `make format`, `make ty`, `make lint-imports` and `make test` clean (100% line and branch coverage), and the docs updated alongside any behaviour change.

## Task 1: Package skeleton, tooling, CI

Flat `zoetty/` package, `pyproject.toml` (hatchling, click, rich, dev group as paulrun plus import-linter), Makefile, `.python-version` 3.14, `.gitignore`, MIT `LICENSE`, CI matrix 3.12-3.15-dev, `CLAUDE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTORS.md`, `CHANGELOG.md`.

- [x] `uv run zoetty --version` prints `zoetty, version 0.1.0`
- [x] `uv build` produces a wheel and sdist

## Task 2: Markup parser (`markup.py`)

- [x] `[bold blue]x[/]`, `[type 1.2]x[/]`, `[type 1.2 0.4]x[/]`, `\[` escapes
- [x] Unknown style raises `MarkupError` naming the style
- [x] `escape()` round-trips through `parse()`

## Task 3: ANSI to markup (`ansi.py`)

- [x] SGR bold/dim/italic, 8 + bright colours, resets (0, 22, 23, 39), 256/truecolour args skipped
- [x] OSC 8 hyperlinks and other OSC stripped; non-SGR CSI dropped
- [x] `\r\n` handled; bare `\r` keeps the last write; trailing blank lines dropped

## Task 4: Clip loading (`clip.py`)

- [x] Loads every key in the spec format with defaults
- [x] Errors (collected, with the key) for: missing `label`, both/neither of `run`/`step`, `output` and `lines` together, unknown keys, unknown theme keys, bad markup, bad `out` extensions, wrong types
- [x] Paths resolved relative to the spec

## Task 5: Timeline (`timeline.py`)

- [x] Runs become typed command lines, output lines, final prompt; duration = end + hold
- [x] Steps pass through
- [x] Missing capture file raises with "run `zoetty record` first"
- [x] Scroll offsets once lines pass `rows`

## Task 6: SVG renderer (`svg.py`)

- [x] Valid XML, `role="img"`, `<title>` = label
- [x] Text at columns with `textLength`; colours, bold, italic, dim
- [x] Typing cover + caret, scrolling, fade, reduced motion, theme, `chrome = false`
- [x] Deterministic

## Task 7: HTML renderer (`html.py`)

- [x] Fragment only, prefixed names, two clips on one page don't clash
- [x] Same features as SVG

## Task 8: `init`, `build`, `check`

- [x] `init` writes a starter spec that builds; refuses to overwrite
- [x] `build` writes every `out` file, reports each
- [x] `check` exits 1 on invalid spec, missing or stale output; 0 when all good

## Task 9: `record`

- [x] Runs setup, then recordable runs, in `[record].cwd` with env, size, pager vars
- [x] Feeds `input`; reports exit codes; timeout stops with an error
- [x] Writes captures, creating folders

## Task 10: Docs and dogfooding

- [x] mkdocs site: home, install, clip format, command line, embedding, examples, agents
- [x] `docs/clips/*.toml` recorded and built by zoetty; test fails if stale
- [x] README: SVG demos from zoetty, quick start, agent prompt section
- [x] HTML fragments embedded in the docs examples page

## Task 11: Release runbook

- [x] `PUBLISHING.md` paulrun runbook (checks, version, tag, GitHub release, docs, PyPI)
- [x] `CHANGELOG.md` 0.1.0 entry, copied to `docs/CHANGELOG.md`
- [x] CI green on GitHub
- [ ] Released to PyPI and docs deployed (Paul, via `paulrun PUBLISHING.md`)
