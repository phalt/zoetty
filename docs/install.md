# 🚀 Install

zoetty is a command-line tool, so install it on its own rather than into a project:

```sh
uv tool install zoetty
```

Or with pip:

```sh
pip install zoetty
```

Check it worked:

```sh
zoetty --version
```

## Requirements

- Python 3.12 or later
- macOS or Linux. `zoetty record` needs a pseudo-terminal, which Windows doesn't have. `zoetty build` and `zoetty check` only read and write files, but are only tested on macOS and Linux.

## In CI

To check clips in CI you only need zoetty itself, not the tools the clips record:

```yaml
- name: Check terminal clips are up to date
  run: uvx zoetty check docs/clips/*.toml
```
