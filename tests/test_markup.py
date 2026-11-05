import pytest

from zoetty.markup import DEFAULT_TYPING_DELAY, MarkupError, Segment, escape, parse, plain


def test_plain_text_is_one_unstyled_segment():
    assert parse("hello") == [Segment("hello")]


def test_empty_markup_has_no_segments():
    assert parse("") == []


def test_styles_apply_until_closed():
    assert parse("[bold blue]1/2[/] Greet") == [Segment("1/2", ("bold", "blue")), Segment(" Greet")]


def test_a_new_style_tag_replaces_the_last():
    assert parse("[red]a[green]b[/]") == [Segment("a", ("red",)), Segment("b", ("green",))]


def test_typing_with_and_without_a_delay():
    assert parse("$ [type 1.2]ls[/]") == [Segment("$ "), Segment("ls", (), 1.2, DEFAULT_TYPING_DELAY)]
    assert parse("[type 0.5 2]y[/]") == [Segment("y", (), 0.5, 2.0)]


def test_escaped_brackets_are_literal():
    assert parse("Start? \\[y/N]") == [Segment("Start? [y/N]")]
    assert plain(parse(escape("[20:37:03] [link]"))) == "[20:37:03] [link]"


@pytest.mark.parametrize(
    "markup, message",
    [
        ("[blink]x[/]", "unknown style '[blink]'"),
        ("[]x", "unknown style '[]'"),
        ("[bold sparkly]x", "unknown style"),
        ("[type]x", "use [type SECONDS]"),
        ("[type 1 2 3]x", "use [type SECONDS]"),
        ("[type fast]x", "needs numbers"),
        ("[type -1]x", "can't be negative"),
    ],
)
def test_bad_markup_says_what_is_wrong(markup, message):
    with pytest.raises(MarkupError, match=message.replace("[", "\\[")):
        parse(markup)


def test_unknown_style_errors_suggest_escaping():
    with pytest.raises(MarkupError, match=r"Write \\\[ for a literal"):
        parse("[20:37:03] hello")
