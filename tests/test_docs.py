"""The docs and README are tested, so they can't drift from what zoetty does."""

import re
from pathlib import Path

import pytest

from zoetty import html, svg, timeline
from zoetty.clip import load

ROOT = Path(__file__).parent.parent
DOCS = ROOT / "docs"
CLIPS = sorted((DOCS / "clips").glob("*.toml"))
PAGES = [ROOT / "README.md", *sorted(DOCS.glob("*.md"))]


def fences(path: Path, language: str) -> list[str]:
    return re.findall(rf"^```{language}\n(.*?)^```", path.read_text(), re.MULTILINE | re.DOTALL)


@pytest.mark.parametrize("path", CLIPS, ids=lambda path: path.name)
def test_docs_clips_are_built_and_up_to_date(path):
    clip = load(path)
    lines = timeline.build(clip)
    for out in clip.out:
        render = svg.render if out.suffix == ".svg" else html.render
        assert out.read_text() == render(clip, lines, timeline.name(out)), (
            f"{out.name} is stale: run `uv run zoetty build {path.relative_to(ROOT)}`"
        )


@pytest.mark.parametrize("page", PAGES, ids=lambda path: path.name)
def test_every_complete_spec_in_the_docs_is_valid(page, tmp_path):
    for number, text in enumerate(fences(page, "toml")):
        if "label =" not in text or "--8<--" in text:
            continue  # a fragment showing a few keys, or an included file tested above
        spec = tmp_path / f"example-{number}.toml"
        spec.write_text(text)
        load(spec)


@pytest.mark.parametrize("page", PAGES, ids=lambda path: path.name)
def test_included_and_linked_clips_exist(page):
    text = page.read_text()
    for name in re.findall(r'^--8<-- "([^"]+)"', text, re.MULTILINE):
        assert (DOCS / name).exists(), name
    for name in re.findall(
        r"\]\((?:https://raw\.githubusercontent\.com/phalt/zoetty/main/docs/)?(clips/[^)]+)\)", text
    ):
        assert (DOCS / name).exists(), name


def test_readme_clips_use_full_urls_so_they_work_on_pypi():
    readme = re.sub(r"^```.*?^```", "", (ROOT / "README.md").read_text(), flags=re.MULTILINE | re.DOTALL)
    images = re.findall(r"!\[[^\]]*\]\(([^)]+\.svg)\)", readme)
    assert images and all(url.startswith("https://raw.githubusercontent.com/phalt/zoetty/main/") for url in images)


def test_the_agent_prompt_is_the_same_everywhere():
    prompts = {
        page.name: fences(page, "text")[0] for page in (ROOT / "README.md", DOCS / "index.md", DOCS / "agents.md")
    }
    assert len(set(prompts.values())) == 1, prompts
    assert "https://phalt.github.io/zoetty/agents/" in prompts["agents.md"]


def test_changelogs_match():
    assert (ROOT / "CHANGELOG.md").read_text() == (DOCS / "CHANGELOG.md").read_text()
