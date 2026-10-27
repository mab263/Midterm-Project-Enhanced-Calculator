"""Color-coded terminal output using Colorama."""

import os
import sys

from colorama import Fore, Style


def colors_enabled(stream=None) -> bool:
    """Colors are on only for a real terminal, and never when NO_COLOR is set."""
    stream = stream if stream is not None else sys.stdout
    if os.environ.get("NO_COLOR"):
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


def _emit(message: str, color: str) -> None:
    if colors_enabled():
        print(f"{color}{message}{Style.RESET_ALL}")
    else:
        print(message)


def success(message: str) -> None:
    """Print a successful result or confirmation in green."""
    _emit(message, Fore.GREEN)


def error(message: str) -> None:
    """Print an error in red."""
    _emit(message, Fore.RED)


def warning(message: str) -> None:
    """Print a hint or recoverable problem in yellow."""
    _emit(message, Fore.YELLOW)


def info(message: str) -> None:
    """Print a heading or general message in cyan."""
    _emit(message, Fore.CYAN)