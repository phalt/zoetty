# 🖼️ Embedding clips

One spec can build both formats:

```toml
out = ["demo.svg", "demo.html"]
```

| | SVG | HTML fragment |
|---|---|---|
| Use it in | READMEs, PyPI, anything that shows images | Docs sites and pages you control |
| How | `![alt](demo.svg)` or `<img>` | Paste or include the file's contents |
| Text | Part of the image | Real text people can select and copy |
| Fonts | The viewer's monospace font | The page's, or a monospace font you load |
| Size | A few KB | A few KB |

Both loop for ever and fade out before restarting, or play a set number of times with [`loop`](clip-format.md#play-once). Both show the finished screen with no animation for people who prefer reduced motion.

## SVG in a README

GitHub strips `<style>` from README HTML, so an HTML clip won't animate there. An SVG referenced as an image does, because its animation is CSS inside the SVG file:

```markdown
![zoetty building a clip](docs/clips/demo.svg)
```

PyPI shows your README too, but it can't follow relative paths. Use the file's full URL on GitHub so the clip works in both places:

```markdown
![zoetty building a clip](https://raw.githubusercontent.com/you/project/main/docs/clips/demo.svg)
```

The image is served from `main`, so it updates when you merge, and a README on an old PyPI release shows the latest clip.

Inside an image, an SVG can't load web fonts, so it uses the viewer's monospace font. zoetty pins every run of text to its column, so the layout holds whichever font that is.

## HTML in a docs site

The `.html` file is a fragment: a `<div>` and a `<style>`, with no `<html>` or `<body>`. Every class and animation name starts with the file's name (`zt-demo-...`), so several clips can share a page.

With MkDocs, include it with the [snippets](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/) extension:

```yaml
# mkdocs.yml
markdown_extensions:
  - pymdownx.snippets:
      base_path: ["docs"]
```

```markdown
;--8<-- "clips/demo.html"
```

This page's [examples](examples.md) are embedded exactly like that. Anything else that lets you put raw HTML in a page works the same way: Hugo shortcodes, Jekyll includes, Astro components, or plain copy and paste.

## Pausing to read

With `pause_on_hover = true`, a clip pauses while the pointer is over its screen, so people can stop it on any frame and read it. It also pauses while it has focus: tab to it with the keyboard, or tap it on a touch screen, and tap elsewhere to carry on.

```toml
pause_on_hover = true
```

This needs the clip to get pointer events. HTML fragments do, and so do SVGs pasted inline into a page. An SVG shown as an image (`![alt](demo.svg)` or `<img>`), which is how READMEs and PyPI show it, gets no pointer events at all, so there it has no effect. To let people read the end of a clip there, use [`loop`](clip-format.md#play-once) instead.

## Replaying a clip

Clips with [`loop`](clip-format.md#play-once) set stop on their final frame. To watch one again, reload the page.

### HTML: the replay button

An HTML clip that stops gets a **↻ Replay** button in its top corner, shown once every play has finished. Click it, or press Space when it has keyboard focus, and the clip starts again from the beginning. There's no JavaScript: while the button is held down the clip's animations are removed, and letting go starts them all again. With `pause_on_hover`, the button's timer pauses along with the clip, so it never shows early.

Two limitations, because it's CSS only:

- Enter doesn't replay. Browsers only treat a button as pressed for Space, so use Space from the keyboard.
- On touch screens, Safari on iOS may not show a button as pressed without JavaScript on the page, so the button might not work there. Reloading the page always replays the clip.

The [examples](examples.md#play-once-pause-and-replay) page has one to try.

### SVG: link the image to itself

An SVG shown as an image gets no clicks, so it can't have a button. Instead, wrap the image in a link to the same file. Clicking it opens the SVG on its own, which plays it from the start:

```markdown
[![zoetty building a clip](https://raw.githubusercontent.com/you/project/main/docs/clips/demo.svg)](https://raw.githubusercontent.com/you/project/main/docs/clips/demo.svg)
```

This works on PyPI as well as GitHub, and in any page that shows Markdown or HTML images.

### Clips start when the page loads

An animation starts when the page loads, not when it's scrolled into view. On a long README, a clip that plays once may have finished before anyone scrolls down to it. They'll still see its final frame, which is often what matters most. If the animation itself matters, give the clip a few plays with `loop = 3`, or keep it near the top of the page.

## Matching your site's colours

Set `[theme]` to your site's code colours, so a clip sits next to your code blocks as if it belonged there:

```toml
[theme]
bg = "#282c34"
bar = "#21252b"
fg = "#abb2bf"
```

## Keeping clips fresh

Commit the spec, the captures and the built files. When the tool a clip shows changes:

```sh
zoetty record docs/clips/*.toml
zoetty build docs/clips/*.toml
git diff docs/clips/
```

And in CI, so a clip can't silently go stale:

```yaml
- name: Check terminal clips are up to date
  run: uvx zoetty check docs/clips/*.toml
```
