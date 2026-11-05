# 🤖 Using zoetty with an agent

zoetty works well with coding agents (Claude Code, Codex, Cursor and others): a clip is a short text file, every command reports what it did, and `zoetty check` tells you when you're done.

## The prompt

Paste this into your agent, in the repo you want a demo for:

```text
Use zoetty to add an animated terminal demo of this project to the README.
Read https://phalt.github.io/zoetty/agents/ first and follow it: install zoetty,
write a clip spec in docs/clips/ that shows the most useful commands, record the
real output with `zoetty record`, build it with `zoetty build`, look at the result,
embed the SVG in README.md, and add `zoetty check docs/clips/*.toml` to CI.
```

Change the first line to ask for something more specific: a clip for one docs page, a REPL session using a library, or replacing an old GIF.

## Instructions for agents

If you're an agent that's been sent here, follow these steps.

1. **Install zoetty** with `uv tool install zoetty` (or `pip install zoetty`). Check with `zoetty --version`.
2. **Decide what the clip shows.** One idea per clip, ideally 2 to 4 commands and under 25 lines of output. Read the project's README and docs to choose the commands a new user would run first.
3. **Write the spec** in `docs/clips/<name>.toml`. Start from `zoetty init docs/clips/<name>.toml` or the [examples](examples.md). Every key is in the [clip format](clip-format.md). In particular:
    - Write a `label` that says what happens in the clip, in a sentence. It's the alt text.
    - Give each command an `output` file under `docs/clips/captures/`, so its real output is recorded. Only use `lines` for output you can't record.
    - Set `cols` to fit the widest output line (usually 72 to 100), and `rows` if there's more output than fits comfortably.
    - Use `[record] setup` to reset anything a command creates (`rm -rf my_output`), so recording again gives the same clip.
    - Use `exec` when the command needs a path or prefix the reader shouldn't see (`.venv/bin/tool`, `uv run tool`, `cd example &&`).
    - Use `input` for anything that prompts or for a REPL. It's sent after the program goes quiet, then Ctrl-D.
4. **Record it**: `zoetty record docs/clips/<name>.toml`. Read the output: every run should be `✓`, or `!` if the command is meant to fail. Open the capture files and check they hold what you expected. Never edit captures by hand: fix the spec or the setup and record again.
5. **Build it**: `zoetty build docs/clips/<name>.toml`.
6. **Look at it.** Open the SVG in a browser, or take screenshots at a few points if you can. Check nothing is cut off at the right edge (raise `cols`), nothing important scrolls away too fast (raise `rows` or `line_gap`), and the timing feels natural.
7. **Embed it.**
    - README: `![<label>](https://raw.githubusercontent.com/<owner>/<repo>/main/docs/clips/<name>.svg)`. A full URL works on GitHub and PyPI.
    - Docs sites: the SVG as an image, or add `.html` to `out` and include the fragment. See [embedding](embedding.md).
8. **Keep it fresh.** Add `zoetty check docs/clips/*.toml` to CI (e.g. `uvx zoetty check docs/clips/*.toml`). Commit the spec, captures and built files together.

### Don'ts

- Don't write output by hand that you could record: the point is that the clip shows what the tool really does.
- Don't put secrets, tokens or personal paths in specs or captures. Check the capture files before committing.
- Don't record commands that change things outside the repo (deploys, publishing, sending messages).

## Updating clips later

When a tool's output changes, the same agent can refresh every clip:

```text
The output of this project's CLI has changed. Re-record and rebuild the zoetty
clips in docs/clips/ (zoetty record, then zoetty build), look at each one, and
make sure `zoetty check docs/clips/*.toml` passes.
```
