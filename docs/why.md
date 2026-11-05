# 💡 Why zoetty

**Tiny terminal demos from real output, kept honest by CI.**

## Demos that can't go stale

Most terminal demos are recorded once and then quietly go wrong. Output messages change, flags get renamed, a command disappears, and the GIF in the README keeps showing the old version until someone notices.

zoetty treats a demo like code:

- `zoetty record` runs your commands for real, in a terminal the size of the clip, and saves exactly what they printed, colours and all.
- The spec, the captured output and the built clip are all committed, so a change to a demo shows up in a diff and gets reviewed like any other change.
- `zoetty check` fails if a built clip doesn't match its spec and captures. Run it in CI and a stale or hand-edited clip can't be merged.

`check` only reads the files in your repo, so CI needs zoetty and nothing else: not your tool, its dependencies, or any credentials it uses. When your tool's output changes, `zoetty record` and `zoetty build` bring every clip up to date in one go.

## Tiny

The clips in these docs are between 4KB and 15KB each. They're text: SVG elements and CSS keyframes, which also compress well. A GIF of the same few seconds is usually measured in megabytes, and still looks blurry on a high-resolution screen. zoetty clips stay sharp at any size, because they're drawn as vectors.

zoetty itself is small too. It's pure Python with two dependencies, [click](https://click.palletsprojects.com/) and [rich](https://rich.readthedocs.io/). There's no ffmpeg, headless browser, Node or Go toolchain to install, locally or in CI:

```sh
uv tool install zoetty
```

## Nothing new to learn

A clip is a short TOML file:

```toml
label = "Listing the files in a project"

[[run]]
cmd = "ls"
output = "captures/ls.ansi"
```

If you've written a `pyproject.toml` or a `Cargo.toml`, you can already read and write one. There's no scripting language to learn, and no keystrokes or sleeps to choreograph: you list the commands, and zoetty works out the typing and timing so the clip feels natural. When you do need control, it's one more key, like `think`, `pause` or `line_gap`. The whole format fits on [one page](clip-format.md).

## Made for agents

Coding agents are good at zoetty, because there's very little to get wrong:

- A spec is a few lines of a format the agent already knows.
- Every command says what it did and where it wrote it, so the agent can check its own work.
- `zoetty check` gives a clear pass or fail, so the agent knows when it's done.
- [A page of these docs](agents.md) is written for agents to follow, step by step.

Paste [the prompt](agents.md#the-prompt) into Claude Code, Codex, Cursor or similar, and you get a recorded, built and embedded demo, plus a CI check to keep it that way. When your output changes later, the same agent can refresh every clip.

## Plays everywhere

One spec builds two formats:

- **SVG** for anywhere that takes an image. It animates on GitHub and PyPI, which strip the styles from HTML in a README but leave an SVG image alone.
- **HTML fragment** for docs sites and pages you control. Text is real text that people can select and copy, and you can put as many clips on one page as you like.

Both are accessible by default. Every clip needs a `label`, which becomes its alt text, so people using screen readers learn what the demo shows. Both formats respect "reduce motion" settings and show the finished screen instead of animating.

See [embedding clips](embedding.md) for the details.

## When to use something else

zoetty is built for command-line tools whose output is printed line by line, which is most of them. It doesn't emulate a full terminal, so it isn't the right choice for everything:

- **Full-screen apps (TUIs), editors, or progress bars that redraw the screen.** Use [VHS](https://github.com/charmbracelet/vhs), which runs a real terminal emulator and records GIF or video.
- **Showing a real session exactly as it happened, pauses and all**, or sharing one with a link. Use [asciinema](https://asciinema.org/).
- **A video for a talk or a social post.** Use VHS, or a screen recorder.

If your demo is a few commands and their output in a README or on a docs site, and you want it to stay right, that's what zoetty is for.
