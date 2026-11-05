# zoetty 0.1.0 tasks

Plan: [tasks/plan.md](plan.md). Spec: [specs/SPEC.md](../specs/SPEC.md).

Every task also clears the standing bar: `make format`, `make ty`, `make lint-imports` and `make test` clean (100% line and branch coverage), and the docs updated alongside any behaviour change.

## Task 1: Package skeleton, tooling, CI

Flat `zoetty/` package, `pyproject.toml` (hatchling, click, rich, dev group as paulrun plus import-linter), Makefile, `.python-version` 3.14, `.gitignore`, MIT `LICENSE`, CI matrix 3.12-3.15-dev, `CLAUDE.md`, `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CONTRIBUTORS.md`, `CHANGELOG.md`.

- [ ] `uv run zoetty --version` prints `zoetty, version 0.1.0`
- [ ] `uv build` produces a wheel and sdist

## Task 2: Markup parser (`markup.py`)

- [ ] `[bold blue]x[/]`, `[type 1.2]x[/]`, `[type 1.2 0.4]x[/]`, `\[` escapes
- [ ] Unknown style raises `MarkupError` naming the style
- [ ] `escape()` round-trips through `parse()`

## Task 3: ANSI to markup (`ansi.py`)

- [ ] SGR bold/dim/italic, 8 + bright colours, resets (0, 22, 23, 39), 256/truecolour args skipped
- [ ] OSC 8 hyperlinks and other OSC stripped; non-SGR CSI dropped
- [ ] `\r\n` handled; bare `\r` keeps the last write; trailing blank lines dropped

## Task 4: Clip loading (`clip.py`)

- [ ] Loads every key in the spec format with defaults
- [ ] Errors (collected, with the key) for: missing `label`, both/neither of `run`/`step`, `output` and `lines` together, unknown keys, unknown theme keys, bad markup, bad `out` extensions, wrong types
- [ ] Paths resolved relative to the spec

## Task 5: Timeline (`timeline.py`)

- [ ] Runs become typed command lines, output lines, final prompt; duration = end + hold
- [ ] Steps pass through
- [ ] Missing capture file raises with "run `zoetty record` first"
- [ ] Scroll offsets once lines pass `rows`

## Task 6: SVG renderer (`svg.py`)

- [ ] Valid XML, `role="img"`, `<title>` = label
- [ ] Text at columns with `textLength`; colours, bold, italic, dim
- [ ] Typing cover + caret, scrolling, fade, reduced motion, theme, `chrome = false`
- [ ] Deterministic

## Task 7: HTML renderer (`html.py`)

- [ ] Fragment only, prefixed names, two clips on one page don't clash
- [ ] Same features as SVG

## Task 8: `init`, `build`, `check`

- [ ] `init` writes a starter spec that builds; refuses to overwrite
- [ ] `build` writes every `out` file, reports each
- [ ] `check` exits 1 on invalid spec, missing or stale output; 0 when all good

## Task 9: `record`

- [ ] Runs setup, then recordable runs, in `[record].cwd` with env, size, pager vars
- [ ] Feeds `input`; reports exit codes; timeout stops with an error
- [ ] Writes captures, creating folders

## Task 10: Docs and dogfooding

- [ ] mkdocs site: home, install, clip format, command line, embedding, examples, agents
- [ ] `docs/clips/*.toml` recorded and built by zoetty; test fails if stale
- [ ] README: SVG demos from zoetty, quick start, agent prompt section
- [ ] HTML fragments embedded in the docs examples page

## Task 11: Release runbook

- [ ] `PUBLISHING.md` paulrun runbook (checks, version, tag, GitHub release, docs, PyPI)
- [ ] `CHANGELOG.md` 0.1.0 entry, copied to `docs/CHANGELOG.md`
- [ ] CI green on GitHub
