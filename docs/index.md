# 🎞️ zoetty

## What is zoetty?

**Tiny terminal demos from real output, kept honest by CI.**

zoetty turns terminal sessions into small, looping, animated clips made of plain SVG or HTML and CSS. No video, no GIF, no JavaScript.

<div style="text-align: center; padding-top:10px;">
<p>
    <a href="https://pypi.org/project/zoetty">
    <img alt="Package version" src="https://img.shields.io/pypi/v/zoetty?color=%2334D058&label=latest%20version">
    </a>
    <img alt="Python versions" src="https://img.shields.io/badge/python-3.12+-blue">
    <img alt="PyPI - License" src="https://img.shields.io/pypi/l/zoetty">
</p>
</div>

--8<-- "clips/quickstart.html"

That's zoetty, recorded by zoetty, and shown here as its HTML output: try selecting the text. Every clip in these docs is built from a spec in [`docs/clips/`](https://github.com/phalt/zoetty/tree/main/docs/clips), and the test suite fails if any of them are out of date.

## Why use zoetty?

- **Demos that can't go stale** - `zoetty record` captures what your commands really print, and `zoetty check` fails CI the moment a clip stops matching. CI doesn't even need your tool installed.
- **Tiny** - Clips are a few KB of text, not megabytes of GIF. zoetty itself is pure Python with two dependencies: no ffmpeg, no browser, no Node.
- **Nothing new to learn** - A clip is a short TOML file, the same format as your `pyproject.toml`. No custom scripting language.
- **Made for agents** - Paste [one prompt](#use-it-with-your-coding-agent) and your coding agent writes, records, builds and checks the clip for you.
- **Plays everywhere** - The SVG works anywhere images do, GitHub and PyPI included. The same spec builds an HTML fragment with selectable text for your docs. Every clip has alt text and respects reduced motion.

[Why zoetty, in more detail](why.md)

## How it works

1. **Describe** the clip in a TOML file: the commands to type, and where their output comes from.
2. **Record** it: `zoetty record` runs the commands in a pseudo-terminal and saves what they print, colours and all, next to the spec.
3. **Build** it: `zoetty build` renders the spec to an `.svg`, an `.html` fragment, or both.
4. **Check** it in CI: `zoetty check` fails if a built clip no longer matches its spec.

Timing is generated, not recorded: commands are typed at a steady speed and output appears line by line, so clips never sit on a long pause or dump everything at once.

## Quick start

```sh
uv tool install zoetty
zoetty init docs/clips/hello.toml    # write a starter spec
zoetty build docs/clips/hello.toml   # render it to docs/clips/hello.svg
```

Then put it in your README like any image:

```markdown
![What the clip shows](docs/clips/hello.svg)
```

Next: [the clip format](clip-format.md), [embedding clips](embedding.md) and [examples](examples.md).

## Use it with your coding agent

Paste this into Claude Code, Codex, Cursor or similar:

```text
Use zoetty to add an animated terminal demo of this project to the README.
Read https://phalt.github.io/zoetty/agents/ first and follow it: install zoetty,
write a clip spec in docs/clips/ that shows the most useful commands, record the
real output with `zoetty record`, build it with `zoetty build`, look at the result,
embed the SVG in README.md, and add `zoetty check docs/clips/*.toml` to CI.
```

See [Using zoetty with an agent](agents.md) for what the agent will follow.
