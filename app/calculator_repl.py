"""Command-line REPL (Read-Eval-Print Loop) for the calculator."""

from typing import Optional

from app.calculator import Calculator
from app.exceptions import CalculatorError
from app.operations import OperationFactory

CANCEL = "cancel"


def show_help(_calc: Calculator) -> None:
    """Print every available command."""
    print("\nAvailable commands:")
    print(f"  {', '.join(OperationFactory.available_operations())} - Perform a calculation")
    print("  history - Show calculation history")
    print("  clear   - Clear calculation history")
    print("  undo    - Undo the last calculation")
    print("  redo    - Redo the last undone calculation")
    print("  save    - Save history to the CSV file")
    print("  load    - Load history from the CSV file")
    print("  help    - Show this message")
    print("  exit    - Exit the calculator")


def show_history(calc: Calculator) -> None:
    lines = calc.show_history()
    if not lines:
        print("No calculations in history")
        return
    print("\nCalculation History:")
    for index, line in enumerate(lines, 1):
        print(f"{index}. {line}")


def clear_history(calc: Calculator) -> None:
    calc.clear_history()
    print("History cleared")


def undo(calc: Calculator) -> None:
    print("Operation undone" if calc.undo() else "Nothing to undo")


def redo(calc: Calculator) -> None:
    print("Operation redone" if calc.redo() else "Nothing to redo")


def save(calc: Calculator) -> None:
    calc.save()
    print("History saved successfully")


def load(calc: Calculator) -> None:
    calc.load()
    print("History loaded successfully")


COMMANDS = {
    "help": show_help,
    "history": show_history,
    "clear": clear_history,
    "undo": undo,
    "redo": redo,
    "save": save,
    "load": load,
}


def ask(prompt: str) -> Optional[str]:
    """Ask for input. Returns None if the user types 'cancel'."""
    value = input(prompt).strip()
    return None if value.lower() == CANCEL else value


def run_calculation(calc: Calculator, name: str) -> None:
    """Prompt for two numbers, then perform the named operation."""
    print(f"Enter two numbers (or '{CANCEL}' to abort):")
    first = ask("First number: ")
    if first is None:
        print("Operation cancelled")
        return
    second = ask("Second number: ")
    if second is None:
        print("Operation cancelled")
        return

    calc.set_operation(OperationFactory.create_operation(name))
    result = calc.perform_operation(first, second)
    print(f"Result: {format(result.normalize(), 'f')}")


def calculator_repl(calc: Optional[Calculator] = None) -> None:
    """Read commands and run them until the user types 'exit'."""
    calc = calc or Calculator()
    print("Calculator started. Type 'help' for commands.")

    while True:
        try:
            command = input("\nEnter command: ").strip().lower()

            if command == "exit":  # LBYL: check for the special commands first
                print("Goodbye!")
                return
            if command in COMMANDS:
                COMMANDS[command](calc)
            elif command in OperationFactory.available_operations():
                run_calculation(calc, command)
            elif command:
                print(f"Unknown command: '{command}'. Type 'help' for available commands.")
        except CalculatorError as error:  # EAFP: try it, handle the failure
            print(f"Error: {error}")
        except KeyboardInterrupt:  # Ctrl+C cancels the current command
            print("\nOperation cancelled")
        except EOFError:  # Ctrl+D or no more input
            print("\nInput ended. Goodbye!")
            return
        except Exception as error:  # last resort, so a bug never kills the session
            print(f"Unexpected error: {error}")