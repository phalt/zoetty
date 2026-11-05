"""Render a clip as an HTML fragment (a <div> and a <style>) for pages you control."""

from html import escape

from zoetty.clip import Clip
from zoetty.timeline import Timeline, percent

FONTS = 'ui-monospace,"JetBrains Mono","SF Mono",Menlo,Consolas,monospace'


def render(clip: Clip, timeline: Timeline, name: str) -> str:
    """The clip as an HTML fragment.

    Text is real, selectable text. Every class and keyframe is prefixed with `name`, so
    several clips can share a page.
    """
    total = timeline.duration
    css: list[str] = []
    body: list[str] = []
    n = name

    for index, line in enumerate(timeline.lines):
        css.append(f"@keyframes {n}-l{index}{{0%{{opacity:0}}{percent(line.at, total)},100%{{opacity:1}}}}")
        parts = []
        clock = line.at
        for position, segment in enumerate(line.segments):
            classes = " ".join(f"{n}-{style}" for style in segment.styles)
            text = escape(segment.text)
            if segment.typing is not None and segment.text:
                length = len(segment.text)
                animation = f"{n}-t{index}-{position}"
                start = clock + segment.delay
                end = start + segment.typing
                css.append(
                    f"@keyframes {animation}{{0%,{percent(start, total)}"
                    f"{{width:0;animation-timing-function:steps({length},end)}}"
                    f"{percent(end, total)},100%{{width:{length}ch}}}}"
                )
                parts.append(f'<span class="{n}-type {classes}" style="animation-name:{animation}">{text}</span>')
                clock = end
            elif classes:
                parts.append(f'<span class="{classes}">{text}</span>')
            else:
                parts.append(text)
        if line.caret_until is not None:
            css.append(
                f"@keyframes {n}-k{index}{{0%{{opacity:0}}{percent(line.at, total)}{{opacity:1}}"
                f"{percent(line.caret_until, total)},100%{{opacity:0}}}}"
            )
            parts.append(f'<span class="{n}-caret" style="animation-name:{n}-k{index}"><i></i></span>')
        body.append(f'<div class="{n}-ln" style="animation-name:{n}-l{index}">{"".join(parts) or "&nbsp;"}</div>')

    stops = "".join(
        f"{percent(at, total)}{{transform:translateY(-{rows * 1.5:g}em)}}" for at, rows in timeline.scroll()
    )
    last = max(len(timeline.lines) - timeline.rows, 0) * 1.5
    css.append(
        f"@keyframes {n}-scroll{{0%{{transform:translateY(0)}}{stops}100%{{transform:translateY(-{last:g}em)}}}}"
    )
    css.append(
        f"@keyframes {n}-fade{{0%{{opacity:1}}{percent(timeline.fade, total)}"
        f"{{opacity:1;animation-timing-function:ease}}100%{{opacity:0}}}}"
    )

    theme = "".join(f"--{key}:{value};" for key, value in clip.theme.items())
    colours = "".join(f".{n}-{c}{{color:var(--{c})}}" for c in ("blue", "green", "yellow", "red", "cyan", "magenta"))
    bar = ""
    if clip.chrome:
        bar = f'<div class="{n}-bar"><span></span><span></span><span></span><b>{escape(clip.title)}</b></div>\n'
    newline = "\n"
    return f"""<div class="{n}" role="img" aria-label="{escape(clip.label)}">
{bar}<div class="{n}-screen" style="animation-name:{n}-fade"><div class="{n}-view"><div class="{n}-body" style="animation-name:{n}-scroll">{"".join(body)}</div></div></div>
</div>
<style>
.{n}{{{theme}font:clamp(9px,1.6vw,14px)/1.5 {FONTS};background:var(--bg);color:var(--fg);border-radius:10px;overflow:hidden;width:min(100%,calc({clip.cols}ch + 3em));box-shadow:0 10px 30px #0006;text-align:left;margin:1.5em 0}}
.{n}-bar{{display:flex;align-items:center;gap:.45em;padding:.6em .9em;background:var(--bar)}}
.{n}-bar span{{width:.8em;height:.8em;border-radius:50%;background:var(--fg);opacity:.3}}
.{n}-bar b{{flex:1;text-align:center;font-weight:400;opacity:.5;margin-right:3em}}
.{n}-screen{{padding:1em 1.5em 1.2em}}
.{n}-view{{height:{timeline.rows * 1.5:g}em;overflow:hidden}}
.{n}-screen,.{n}-body,.{n}-ln,.{n}-type,.{n}-caret{{animation-duration:{total}s;animation-iteration-count:infinite;animation-timing-function:step-end}}
.{n}-ln{{white-space:pre;opacity:0}}
.{n}-type{{display:inline-block;vertical-align:bottom;overflow:hidden;width:0}}
.{n}-caret{{opacity:0}}
.{n}-caret i{{display:inline-block;width:.6em;height:1.15em;vertical-align:-.2em;background:var(--fg);animation:{n}-blink 1s step-end infinite}}
@keyframes {n}-blink{{50%{{opacity:0}}}}
.{n}-dim{{opacity:.55}}.{n}-bold{{font-weight:700}}.{n}-italic{{font-style:italic}}{colours}
{newline.join(css)}
@media (prefers-reduced-motion:reduce){{.{n} *{{animation:none!important}}.{n}-ln{{opacity:1}}.{n}-type{{width:auto}}.{n}-caret{{display:none}}.{n}-body{{transform:translateY(-{last:g}em)}}}}
</style>
"""
