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

Both loop for ever, fade out before restarting, and show the finished screen with no animation for people who prefer reduced motion.

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
