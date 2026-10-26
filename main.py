"""Entry point for the calculator application."""

import sys

from app.calculator_repl import calculator_repl
from app.exceptions import CalculatorError


def main() -> int:
    try:
        calculator_repl()
    except CalculatorError as error:  # e.g., an invalid .env setting at startup
        print(f"Could not start the calculator: {error}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())