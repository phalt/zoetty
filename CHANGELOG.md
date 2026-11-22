# Change log

## 0.2.0

- `loop = false` plays a clip once and `loop = 3` plays it three times, then it stays on its final frame so people can read the end.
- `pause_on_hover = true` pauses an HTML clip or inline SVG while the pointer is over it or it has focus.
- HTML clips that stop show a CSS-only replay button once they finish.
- 17 theme presets from Ghostty's themes, such as Catppuccin, Dracula, Monokai, Nord, Gruvbox and Solarized: `theme = "dracula"`, or `[theme]` with `name = "dracula"` to change some of its colours.
- `zoetty themes` lists the presets; `zoetty themes NAME` prints one as a `[theme]` table to paste and edit.
- A themes page in the docs: every preset, the default colours, and the CSS variables and classes for restyling HTML clips from your own stylesheet.

## 0.1.0

The first release.

- `zoetty init`, `record`, `build` and `check`.
- Clip specs in TOML: `[[run]]` sessions with recorded or hand-written output, or hand-timed `[[step]]`s.
- `zoetty record` runs commands in a pseudo-terminal the size of the clip, keeps their colours, types `input` after each prompt and ends with Ctrl-D.
- SVG output for READMEs and anywhere that takes images; HTML fragments for docs sites, safe to put several on one page.
- Long output wraps at `cols` and scrolls past `rows`. `[theme]` colours, optional window chrome, and reduced-motion support.
