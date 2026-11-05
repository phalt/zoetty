"""Render a clip as one animated SVG, for anywhere that takes an image (READMEs, PyPI)."""

from html import escape

from zoetty.clip import Clip
from zoetty.markup import COLOURS
from zoetty.timeline import Timeline, percent

FONT_SIZE = 14
LINE_HEIGHT = 21
CHAR_WIDTH = FONT_SIZE * 0.6
PAD_X, PAD_Y = 24, 18
BAR = 34
FONTS = 'ui-monospace,"SF Mono",Menlo,Consolas,"DejaVu Sans Mono","Liberation Mono",monospace'


def render(clip: Clip, timeline: Timeline, name: str) -> str:
    """The clip as an SVG document.

    Every text run is pinned to its column with textLength, so alignment holds whatever
    monospace font the viewer falls back to (an <img> can't load web fonts). Typing is a
    background-coloured cover that slides right in steps, carrying the caret with it.
    """
    theme = clip.theme
    total = timeline.duration
    bar = BAR if clip.chrome else 0
    top = bar + PAD_Y
    width = round(clip.cols * CHAR_WIDTH + PAD_X * 2)
    height = round(top + PAD_Y + timeline.rows * LINE_HEIGHT)
    css: list[str] = []
    body: list[str] = []

    for index, line in enumerate(timeline.lines):
        y = top + index * LINE_HEIGHT
        baseline = y + LINE_HEIGHT * 0.75
        css.append(f"@keyframes {name}-l{index}{{0%{{opacity:0}}{percent(line.at, total)},100%{{opacity:1}}}}")
        texts: list[str] = []
        covers: list[tuple[str, float, float]] = []
        column, clock = 0, line.at
        for segment in line.segments:
            length = len(segment.text)
            stripped = segment.text.rstrip()
            lead = len(stripped) - len(stripped.lstrip())
            stripped = stripped.lstrip()
            if stripped:
                attributes = [
                    f'x="{PAD_X + (column + lead) * CHAR_WIDTH:.1f}"',
                    f'y="{baseline:.1f}"',
                    f'textLength="{len(stripped) * CHAR_WIDTH:.1f}"',
                    'lengthAdjust="spacingAndGlyphs"',
                ]
                for style in segment.styles:
                    if style in COLOURS:
                        attributes.append(f'fill="{theme[style]}"')
                    elif style == "bold":
                        attributes.append('font-weight="700"')
                    elif style == "italic":
                        attributes.append('font-style="italic"')
                    else:
                        attributes.append('opacity=".55"')
                texts.append(f"<text {' '.join(attributes)}>{escape(stripped)}</text>")
            if segment.typing is not None and length:
                start = clock + segment.delay
                end = start + segment.typing
                animation = f"{name}-t{index}-{column}"
                shift = length * CHAR_WIDTH
                css.append(
                    f"@keyframes {animation}{{0%,{percent(start, total)}"
                    f"{{transform:translateX(0);animation-timing-function:steps({length},end)}}"
                    f"{percent(end, total)},100%{{transform:translateX({shift:.1f}px)}}}}"
                )
                covers.append((animation, PAD_X + column * CHAR_WIDTH, shift))
                clock = end
            column += length
        body.append(f'<g class="a" style="animation-name:{name}-l{index}">{"".join(texts)}')
        for animation, x, shift in covers:
            body.append(
                f'<g class="a cover" style="animation-name:{animation}">'
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{shift + CHAR_WIDTH:.1f}" height="{LINE_HEIGHT}"'
                f' fill="{theme["bg"]}"/></g>'
            )
        body.append("</g>")
        if line.caret_until is not None:
            x = PAD_X + column * CHAR_WIDTH
            ride = ""
            if covers:  # the caret starts where the last typed text starts, and rides its cover
                animation, x, _ = covers[-1]
                ride = f' class="a" style="animation-name:{animation}"'
            css.append(
                f"@keyframes {name}-k{index}{{0%{{opacity:0}}{percent(line.at, total)}{{opacity:1}}"
                f"{percent(line.caret_until, total)},100%{{opacity:0}}}}"
            )
            body.append(
                f'<g class="a caret" style="animation-name:{name}-k{index}"><g{ride}>'
                f'<rect class="blink" x="{x:.1f}" y="{y + 2:.1f}" width="{CHAR_WIDTH:.1f}"'
                f' height="{LINE_HEIGHT - 4}" fill="{theme["fg"]}"/></g></g>'
            )

    stops = "".join(
        f"{percent(at, total)}{{transform:translateY(-{rows * LINE_HEIGHT}px)}}" for at, rows in timeline.scroll()
    )
    last = max(len(timeline.lines) - timeline.rows, 0) * LINE_HEIGHT
    css.append(
        f"@keyframes {name}-scroll{{0%{{transform:translateY(0)}}{stops}100%{{transform:translateY(-{last}px)}}}}"
    )
    css.append(
        f"@keyframes {name}-fade{{0%{{opacity:1}}{percent(timeline.fade, total)}"
        f"{{opacity:1;animation-timing-function:ease}}100%{{opacity:0}}}}"
    )

    label = escape(clip.label)
    chrome = ""
    if clip.chrome:
        dots = "".join(
            f'<circle cx="{18 + k * 18}" cy="{BAR / 2}" r="5.5" fill="{theme["fg"]}" opacity=".3"/>' for k in range(3)
        )
        chrome = (
            f'<path d="M0 10a10 10 0 0 1 10-10h{width - 20}a10 10 0 0 1 10 10v{BAR - 10}h-{width}z" fill="{theme["bar"]}"/>'
            f"{dots}"
            f'<text x="{width / 2}" y="{BAR / 2 + 5}" text-anchor="middle" opacity=".5" fill="{theme["fg"]}"'
            f' style="font-size:13px">{escape(clip.title)}</text>'
        )
    newline = "\n"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{label}">
<title>{label}</title>
<style>
text{{font-family:{FONTS};font-size:{FONT_SIZE}px;white-space:pre}}
.a{{animation-duration:{total}s;animation-iteration-count:infinite;animation-timing-function:step-end}}
.blink{{animation:{name}-blink 1s step-end infinite}}
@keyframes {name}-blink{{50%{{opacity:0}}}}
{newline.join(css)}
@media (prefers-reduced-motion:reduce){{.a,.blink{{animation:none!important}}.cover,.caret{{display:none}}.scroll{{transform:translateY(-{last}px)}}}}
</style>
<defs><clipPath id="{name}-screen"><rect x="0" y="{top}" width="{width}" height="{timeline.rows * LINE_HEIGHT}"/></clipPath></defs>
<rect width="{width}" height="{height}" rx="10" fill="{theme["bg"]}"/>
{chrome}
<g clip-path="url(#{name}-screen)" fill="{theme["fg"]}"><g class="a" style="animation-name:{name}-fade"><g class="a scroll" style="animation-name:{name}-scroll">
{newline.join(body)}
</g></g></g>
</svg>
"""
