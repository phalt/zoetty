import textwrap
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def in_tmp_path(tmp_path, monkeypatch):
    """Every test starts in its own folder, so nothing a test writes lands in the repo."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("FORCE_COLOR", raising=False)


@pytest.fixture
def spec(tmp_path):
    """Write a clip spec into the test's folder and return its path."""

    def write(text: str, name: str = "clip.toml") -> Path:
        path = tmp_path / name
        path.write_text(textwrap.dedent(text))
        return path

    return write
