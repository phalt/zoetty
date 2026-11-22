"""Theme colours: zoetty's default and presets of common terminal and editor themes.

Presets follow Ghostty's bundled themes (from iTerm2-Color-Schemes): `background` and
`foreground` are `bg` and `fg`, and palette 1-6 are red, green, yellow, blue, magenta and cyan.
Ghostty has no window bar colour, so `bar` is each theme's own darker (or lighter) surface.
"""

DEFAULT = {
    "bg": "#1c1c1c",
    "fg": "#d0d0d0",
    "bar": "#2a2a2a",
    "blue": "#4b8fe3",
    "green": "#2fcf7a",
    "yellow": "#e6e04a",
    "red": "#e05252",
    "cyan": "#4fc6d6",
    "magenta": "#c678dd",
}

# Ghostty's name for each theme is in its comment.
PRESETS = {
    # Catppuccin Latte
    "catppuccin-latte": {
        "bg": "#eff1f5",
        "fg": "#4c4f69",
        "bar": "#e6e9ef",
        "red": "#d20f39",
        "green": "#40a02b",
        "yellow": "#df8e1d",
        "blue": "#1e66f5",
        "magenta": "#ea76cb",
        "cyan": "#179299",
    },
    # Catppuccin Mocha
    "catppuccin-mocha": {
        "bg": "#1e1e2e",
        "fg": "#cdd6f4",
        "bar": "#181825",
        "red": "#f38ba8",
        "green": "#a6e3a1",
        "yellow": "#f9e2af",
        "blue": "#89b4fa",
        "magenta": "#f5c2e7",
        "cyan": "#94e2d5",
    },
    # Dracula
    "dracula": {
        "bg": "#282a36",
        "fg": "#f8f8f2",
        "bar": "#21222c",
        "red": "#ff5555",
        "green": "#50fa7b",
        "yellow": "#f1fa8c",
        "blue": "#bd93f9",
        "magenta": "#ff79c6",
        "cyan": "#8be9fd",
    },
    # Everforest Dark Hard
    "everforest": {
        "bg": "#1e2326",
        "fg": "#d3c6aa",
        "bar": "#272e33",
        "red": "#e67e80",
        "green": "#a7c080",
        "yellow": "#dbbc7f",
        "blue": "#7fbbb3",
        "magenta": "#d699b6",
        "cyan": "#83c092",
    },
    # GitHub Dark Default
    "github-dark": {
        "bg": "#0d1117",
        "fg": "#e6edf3",
        "bar": "#161b22",
        "red": "#ff7b72",
        "green": "#3fb950",
        "yellow": "#d29922",
        "blue": "#58a6ff",
        "magenta": "#bc8cff",
        "cyan": "#39c5cf",
    },
    # GitHub Light Default
    "github-light": {
        "bg": "#ffffff",
        "fg": "#1f2328",
        "bar": "#f6f8fa",
        "red": "#cf222e",
        "green": "#116329",
        "yellow": "#4d2d00",
        "blue": "#0969da",
        "magenta": "#8250df",
        "cyan": "#1b7c83",
    },
    # Gruvbox Dark
    "gruvbox-dark": {
        "bg": "#282828",
        "fg": "#ebdbb2",
        "bar": "#1d2021",
        "red": "#cc241d",
        "green": "#98971a",
        "yellow": "#d79921",
        "blue": "#458588",
        "magenta": "#b16286",
        "cyan": "#689d6a",
    },
    # Gruvbox Light
    "gruvbox-light": {
        "bg": "#fbf1c7",
        "fg": "#3c3836",
        "bar": "#ebdbb2",
        "red": "#cc241d",
        "green": "#98971a",
        "yellow": "#d79921",
        "blue": "#458588",
        "magenta": "#b16286",
        "cyan": "#689d6a",
    },
    # Kanagawa Wave
    "kanagawa": {
        "bg": "#1f1f28",
        "fg": "#dcd7ba",
        "bar": "#16161d",
        "red": "#c34043",
        "green": "#76946a",
        "yellow": "#c0a36e",
        "blue": "#7e9cd8",
        "magenta": "#957fb8",
        "cyan": "#6a9589",
    },
    # Monokai Classic: like a terminal running it, "blue" is Monokai's orange.
    "monokai-classic": {
        "bg": "#272822",
        "fg": "#fdfff1",
        "bar": "#1e1f1c",
        "red": "#f92672",
        "green": "#a6e22e",
        "yellow": "#e6db74",
        "blue": "#fd971f",
        "magenta": "#ae81ff",
        "cyan": "#66d9ef",
    },
    # Monokai Pro
    "monokai-pro": {
        "bg": "#2d2a2e",
        "fg": "#fcfcfa",
        "bar": "#221f22",
        "red": "#ff6188",
        "green": "#a9dc76",
        "yellow": "#ffd866",
        "blue": "#fc9867",
        "magenta": "#ab9df2",
        "cyan": "#78dce8",
    },
    # Nord
    "nord": {
        "bg": "#2e3440",
        "fg": "#d8dee9",
        "bar": "#3b4252",
        "red": "#bf616a",
        "green": "#a3be8c",
        "yellow": "#ebcb8b",
        "blue": "#81a1c1",
        "magenta": "#b48ead",
        "cyan": "#88c0d0",
    },
    # Atom One Dark
    "one-dark": {
        "bg": "#21252b",
        "fg": "#abb2bf",
        "bar": "#181a1f",
        "red": "#e06c75",
        "green": "#98c379",
        "yellow": "#e5c07b",
        "blue": "#61afef",
        "magenta": "#c678dd",
        "cyan": "#56b6c2",
    },
    # Rose Pine
    "rose-pine": {
        "bg": "#191724",
        "fg": "#e0def4",
        "bar": "#1f1d2e",
        "red": "#eb6f92",
        "green": "#31748f",
        "yellow": "#f6c177",
        "blue": "#9ccfd8",
        "magenta": "#c4a7e7",
        "cyan": "#ebbcba",
    },
    # iTerm2 Solarized Dark
    "solarized-dark": {
        "bg": "#002b36",
        "fg": "#839496",
        "bar": "#073642",
        "red": "#dc322f",
        "green": "#859900",
        "yellow": "#b58900",
        "blue": "#268bd2",
        "magenta": "#d33682",
        "cyan": "#2aa198",
    },
    # iTerm2 Solarized Light
    "solarized-light": {
        "bg": "#fdf6e3",
        "fg": "#657b83",
        "bar": "#eee8d5",
        "red": "#dc322f",
        "green": "#859900",
        "yellow": "#b58900",
        "blue": "#268bd2",
        "magenta": "#d33682",
        "cyan": "#2aa198",
    },
    # TokyoNight
    "tokyo-night": {
        "bg": "#1a1b26",
        "fg": "#c0caf5",
        "bar": "#16161e",
        "red": "#f7768e",
        "green": "#9ece6a",
        "yellow": "#e0af68",
        "blue": "#7aa2f7",
        "magenta": "#bb9af7",
        "cyan": "#7dcfff",
    },
}
