import re

import pytest

from zoetty.markup import COLOURS
from zoetty.themes import DEFAULT, PRESETS

KEYS = {"bg", "fg", "bar", *COLOURS}


def test_the_default_has_every_theme_key():
    assert set(DEFAULT) == KEYS


def test_the_common_ide_themes_are_there():
    assert list(PRESETS) == [
        "catppuccin-latte",
        "catppuccin-mocha",
        "dracula",
        "everforest",
        "github-dark",
        "github-light",
        "gruvbox-dark",
        "gruvbox-light",
        "kanagawa",
        "monokai-classic",
        "monokai-pro",
        "nord",
        "one-dark",
        "rose-pine",
        "solarized-dark",
        "solarized-light",
        "tokyo-night",
    ]


@pytest.mark.parametrize("name", PRESETS)
def test_every_preset_has_exactly_the_theme_keys_as_hex_colours(name):
    theme = PRESETS[name]
    assert set(theme) == KEYS
    assert all(re.fullmatch(r"#[0-9a-f]{6}", value) for value in theme.values()), theme


def test_presets_follow_ghostty():
    # Ghostty's Dracula: background, foreground and palette 1-6.
    assert PRESETS["dracula"] == {
        "bg": "#282a36",
        "fg": "#f8f8f2",
        "bar": "#21222c",
        "red": "#ff5555",
        "green": "#50fa7b",
        "yellow": "#f1fa8c",
        "blue": "#bd93f9",
        "magenta": "#ff79c6",
        "cyan": "#8be9fd",
    }
