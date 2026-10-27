import pytest
from colorama import Fore, Style

from app import output


class FakeStream:
    """A stand-in for sys.stdout that says whether it is a terminal."""

    def __init__(self, is_terminal):
        self._is_terminal = is_terminal

    def isatty(self):
        return self._is_terminal


@pytest.mark.parametrize(
    "is_terminal, no_color, expected",
    [(False, None, False), (True, None, True), (True, "1", False)],
)
def test_colors_enabled(monkeypatch, is_terminal, no_color, expected):
    monkeypatch.delenv("NO_COLOR", raising=False)
    if no_color:
        monkeypatch.setenv("NO_COLOR", no_color)
    assert output.colors_enabled(FakeStream(is_terminal)) is expected


def test_stream_without_isatty_is_not_a_terminal():
    assert output.colors_enabled(object()) is False


@pytest.mark.parametrize(
    "function, color",
    [
        (output.success, Fore.GREEN),
        (output.error, Fore.RED),
        (output.warning, Fore.YELLOW),
        (output.info, Fore.CYAN),
    ],
)
def test_messages_are_colored_in_a_terminal(monkeypatch, capsys, function, color):
    monkeypatch.setattr(output, "colors_enabled", lambda stream=None: True)
    function("hello")
    assert capsys.readouterr().out == f"{color}hello{Style.RESET_ALL}\n"


@pytest.mark.parametrize(
    "function", [output.success, output.error, output.warning, output.info]
)
def test_messages_are_plain_when_not_a_terminal(capsys, function):
    function("hello")
    assert capsys.readouterr().out == "hello\n"