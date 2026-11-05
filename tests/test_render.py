"""Tests for both renderers. They take the same clip, so most checks run against each."""

import re
import xml.etree.ElementTree as ElementTree

import pytest

from zoetty import html, svg, timeline
from zoetty.clip import load

SPEC = """
title = "~/demo <&>"
label = "A demo & <friends>"
cols = 40
rows = 3

[theme]
green = "#00ff00"

[[run]]
cmd = "tool --go"
lines = ["[green]ok[/]  [bold]1[/] [italic]2[/] [dim]3[/] [red]4[/] <tag>", "", "   indented"]

[[run]]
cmd = "tool --stop"
"""


@pytest.fixture
def clip(spec):
    return load(spec(SPEC))


@pytest.fixture
def lines(clip):
    return timeline.build(clip)


def test_svg_is_a_valid_standalone_image(clip, lines):
    out = svg.render(clip, lines, "zt-demo")
    root = ElementTree.fromstring(out)
    namespace = "{http://www.w3.org/2000/svg}"
    assert root.tag == f"{namespace}svg" and root.get("role") == "img"
    assert root.get("aria-label") == "A demo & <friends>"
    assert root.findtext(f"{namespace}title") == "A demo & <friends>"
    assert "<script" not in out and "foreignObject" not in out and "@import" not in out and "url(http" not in out


def test_svg_places_text_at_columns_with_styles(clip, lines):
    out = svg.render(clip, lines, "zt-demo")
    # "ok" is at column 0 of the first output line, "1" at column 4, "indented" at column 3.
    assert re.search(r'<text x="24\.0" [^>]*textLength="16\.8"[^>]*fill="#00ff00">ok</text>', out)
    assert re.search(r'<text x="57\.6" [^>]*font-weight="700">1</text>', out)
    assert 'font-style="italic">2</text>' in out and 'opacity=".55">3</text>' in out
    assert 'fill="#e05252">4</text>' in out and "&lt;tag&gt;" in out
    assert re.search(r'<text x="49\.2" [^>]*>indented</text>', out)


def test_svg_types_commands_and_scrolls(clip, lines):
    out = svg.render(clip, lines, "zt-demo")
    assert "steps(9,end)" in out  # "tool --go" is typed in 9 steps
    assert 'class="a cover"' in out and 'class="a caret"' in out
    # 6 lines in 3 rows: the screen scrolls 3 times, the last 63px (3 rows of 21).
    assert out.count("translateY(-") >= 4 and "translateY(-63px)" in out
    assert "prefers-reduced-motion" in out


def test_svg_without_chrome_is_shorter(spec):
    clip = load(spec(SPEC.replace("rows = 3", "rows = 3\nchrome = false")))
    out = svg.render(clip, timeline.build(clip), "zt-demo")
    assert "<circle" not in out and "~/demo" not in out
    assert 'height="99"' in out  # padding 18 + 3 rows of 21 + padding 18, and no 34px bar


def test_html_is_a_fragment_with_prefixed_names(clip, lines):
    out = html.render(clip, lines, "zt-demo")
    assert out.startswith('<div class="zt-demo" role="img" aria-label="A demo &amp; &lt;friends&gt;">')
    assert "<html" not in out and "<script" not in out
    assert "~/demo &lt;&amp;&gt;" in out
    for name in re.findall(r"@keyframes ([\w-]+)", out):
        assert name.startswith("zt-demo-")
    for name in re.findall(r'class="([^"]+)"', out):
        assert all(part.startswith("zt-demo") for part in name.split())
    assert '<span class="zt-demo-green">ok</span>' in out and "--green:#00ff00;" in out
    assert "steps(9,end)" in out and "width:9ch" in out
    assert "&nbsp;" in out  # the blank output line still takes up a row
    assert "translateY(-3em)" in out and "height:4.5em" in out


def test_html_without_chrome(spec):
    clip = load(spec(SPEC.replace("rows = 3", "rows = 3\nchrome = false")))
    assert 'class="zt-x-bar"' not in html.render(clip, timeline.build(clip), "zt-x")


def test_two_clips_on_one_page_share_no_names(clip, lines):
    first = set(re.findall(r"zt-[\w-]+", html.render(clip, lines, "zt-one")))
    second = set(re.findall(r"zt-[\w-]+", html.render(clip, lines, "zt-two")))
    assert first and second and not first & second


@pytest.mark.parametrize("render", [svg.render, html.render])
def test_rendering_is_deterministic(clip, render):
    assert render(clip, timeline.build(clip), "zt-x") == render(clip, timeline.build(clip), "zt-x")


@pytest.mark.parametrize("render", [svg.render, html.render])
def test_typed_text_in_steps(spec, render):
    clip = load(
        spec(
            """
            label = "x"
            [[step]]
            at = 0
            lines = ["Start? [type 0.1 0.8]y[/] [type 0.2]n[/]"]
            caret = true
            """
        )
    )
    out = render(clip, timeline.build(clip), "zt-x")
    assert out.count("steps(1,end)") == 2
