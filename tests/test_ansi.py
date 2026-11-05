from zoetty.ansi import to_markup

ESC = "\x1b"


def test_plain_output_is_unchanged_apart_from_trailing_space():
    assert to_markup("hello   \nworld\n") == ["hello", "world"]


def test_colours_and_attributes():
    raw = f"{ESC}[1;36m18{ESC}[0m schemas{ESC}[33m...{ESC}[0m {ESC}[2mcli.py{ESC}[0m"
    assert to_markup(raw) == ["[bold cyan]18[/] schemas[yellow]...[/] [dim]cli.py[/]"]


def test_bright_colours_map_to_the_same_names():
    assert to_markup(f"{ESC}[92mok{ESC}[0m") == ["[green]ok[/]"]


def test_italic_and_resets():
    raw = f"{ESC}[3;1;31ma{ESC}[22mb{ESC}[23mc{ESC}[39md"
    assert to_markup(raw) == ["[bold italic red]a[/][italic red]b[/][red]c[/]d"]


def test_default_colours_clear_the_colour():
    for code in (30, 37, 90, 97):
        assert to_markup(f"{ESC}[31m{ESC}[{code}mx") == ["x"]


def test_256_and_truecolour_arguments_are_skipped_not_misread():
    # 38;5;1 must not turn on bold (1); 38;2;1;2;3 must not turn on bold, dim or italic.
    assert to_markup(f"{ESC}[38;5;1;32mx") == ["[green]x[/]"]
    assert to_markup(f"{ESC}[38;2;1;2;3;33mx") == ["[yellow]x[/]"]
    assert to_markup(f"{ESC}[48;5;200mx") == ["x"]


def test_empty_sgr_is_a_reset():
    assert to_markup(f"{ESC}[1mx{ESC}[my") == ["[bold]x[/]y"]


def test_whitespace_is_not_wrapped_in_styles():
    assert to_markup(f"{ESC}[2m   {ESC}[0mx") == ["   x"]


def test_brackets_in_output_are_escaped():
    assert to_markup(f"{ESC}[2;36m[20:37:03]{ESC}[0m hi") == ["[dim cyan]\\[20:37:03][/] hi"]


def test_hyperlinks_and_other_escape_codes_are_dropped():
    raw = f"{ESC}]8;id=1;file:///x.py{ESC}\\cli.py{ESC}]8;;{ESC}\\:89 {ESC}]0;title\x07{ESC}[K{ESC}[?25lok"
    assert to_markup(raw) == ["cli.py:89 ok"]


def test_carriage_returns():
    assert to_markup("a\r\nb\r\n") == ["a", "b"]
    assert to_markup("spinning |\rspinning /\rdone      \n") == ["done"]


def test_trailing_blank_lines_are_dropped_but_inner_ones_kept():
    assert to_markup("a\n\nb\n\n\n") == ["a", "", "b"]
    assert to_markup("") == []


def test_unsupported_codes_like_underline_are_ignored():
    assert to_markup(f"{ESC}[4;32mx{ESC}[24m") == ["[green]x[/]"]
