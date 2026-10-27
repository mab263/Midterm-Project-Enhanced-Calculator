"""Command-line REPL (Read-Eval-Print Loop) for the calculator."""

from typing import Optional

from app import output
from app.calculator import Calculator
from app.commands import parse_command
from app.exceptions import CalculatorError


def calculator_repl(calc: Optional[Calculator] = None) -> None:
    """Read a line, turn it into a Command, and execute it until the user exits."""
    calc = calc or Calculator()
    output.info("Calculator started. Type 'help' for commands.")

    while True:
        try:
            command = parse_command(input("\nEnter command: "))
            if command is None:  # blank line
                continue
            command.execute(calc)
            if command.ends_session:
                return
        except CalculatorError as error:  # EAFP: try it, handle the failure
            output.error(f"Error: {error}")
        except KeyboardInterrupt:  # Ctrl+C cancels the current command
            output.warning("\nOperation cancelled")
        except EOFError:  # Ctrl+D or no more input
            output.info("\nInput ended. Goodbye!")
            return
        except Exception as error:  # last resort, so a bug never kills the session
            output.error(f"Unexpected error: {error}")